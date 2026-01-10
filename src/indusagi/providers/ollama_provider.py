"""
Ollama provider implementation.

Handles API calls to Ollama cloud API (https://ollama.com).
"""

import json
import hashlib
from typing import List, Dict, Any, Optional, Iterator
from ollama import Client, Options, ResponseError
from .base import BaseProvider, ProviderResponse, ToolCall, ProviderStreamEvent


class OllamaProvider(BaseProvider):
    """
    Ollama Cloud API provider implementation.

    Handles communication with Ollama's cloud API using the official Python SDK.
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize Ollama provider for cloud API.

        Args:
            api_key: Ollama API key for cloud authentication
            base_url: API endpoint (defaults to 'https://ollama.com')

        Raises:
            ValueError: If api_key is not provided
        """
        if not api_key:
            raise ValueError(
                "OLLAMA_API_KEY is required for cloud Ollama. "
                "Please set it with: export OLLAMA_API_KEY='your-key-here'"
            )

        # Default to cloud endpoint
        if not base_url:
            base_url = "https://ollama.com"

        # Initialize Ollama client with authorization header
        self.client = Client(
            host=base_url,
            headers={'Authorization': f'Bearer {api_key}'}
        )
        self.api_key = api_key
        self.base_url = base_url

    def create_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: 'AgentConfig',
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> ProviderResponse:
        """
        Create a completion using Ollama's cloud API.

        Args:
            messages: Conversation messages in OpenAI format
            system_prompt: System instructions
            config: Agent configuration
            tools: Optional tool schemas in OpenAI format

        Returns:
            Normalized ProviderResponse

        Raises:
            Exception: If API call fails
        """
        try:
            # Build Ollama-compatible messages
            ollama_messages = self._build_ollama_messages(messages, system_prompt)

            # Build Ollama options from config
            options = self._build_ollama_options(config)

            # Build API parameters
            api_params = {
                "model": config.model,
                "messages": ollama_messages,
                "stream": False
            }

            # Add options if any
            if options:
                api_params["options"] = options

            # Add tools if provided (Ollama uses OpenAI format)
            if tools:
                api_params["tools"] = tools

            # Call Ollama API
            response = self.client.chat(**api_params)

            # Normalize and return response
            return self._normalize_response(response)

        except ResponseError as e:
            # Handle specific HTTP errors
            if e.status_code == 401:
                raise Exception("Invalid OLLAMA_API_KEY. Check your API key at https://ollama.com")
            elif e.status_code == 404:
                raise Exception(f"Model '{config.model}' not available on cloud API. Try: glm-4.7, llama3.1, etc.")
            elif e.status_code == 429:
                raise Exception("Rate limit exceeded. Please wait before retrying.")
            else:
                raise Exception(f"Ollama API error: {str(e)}")
        except ConnectionError:
            raise Exception("Cannot connect to Ollama cloud API at https://ollama.com. Check your internet connection.")
        except Exception as e:
            raise Exception(f"Ollama provider error: {str(e)}")

    def create_streaming_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: 'AgentConfig',
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Iterator[ProviderStreamEvent]:
        """
        Create a streaming completion using Ollama's cloud API.

        Args:
            messages: Conversation messages
            system_prompt: System instructions
            config: Agent configuration
            tools: Optional tool schemas

        Yields:
            ProviderStreamEvent objects

        Raises:
            Exception: If API call fails
        """
        try:
            # Build messages and options
            ollama_messages = self._build_ollama_messages(messages, system_prompt)
            options = self._build_ollama_options(config)

            # Build API parameters
            api_params = {
                "model": config.model,
                "messages": ollama_messages,
                "stream": True
            }

            if options:
                api_params["options"] = options

            if tools:
                api_params["tools"] = tools

            # Stream response
            stream = self.client.chat(**api_params)

            for chunk in stream:
                # Yield content deltas
                if chunk.message.content:
                    yield ProviderStreamEvent(
                        type="content",
                        content=chunk.message.content
                    )

                # Yield tool calls (typically arrive in final chunk)
                if chunk.message.tool_calls:
                    for tc in chunk.message.tool_calls:
                        # Parse arguments if it's a JSON string
                        arguments = tc.function.arguments
                        if isinstance(arguments, str):
                            arguments = json.loads(arguments)

                        yield ProviderStreamEvent(
                            type="tool_call",
                            tool_call=ToolCall(
                                id=self._generate_tool_call_id(tc.function.name, arguments),
                                name=tc.function.name,
                                arguments=arguments
                            )
                        )

                # Yield done event
                if chunk.done:
                    # If tool calls exist, finish_reason should be "tool_calls"
                    if chunk.message.tool_calls:
                        finish_reason = "tool_calls"
                    else:
                        finish_reason = self._normalize_finish_reason(chunk.done_reason if hasattr(chunk, 'done_reason') else None)
                    yield ProviderStreamEvent(
                        type="done",
                        finish_reason=finish_reason
                    )

        except ResponseError as e:
            if e.status_code == 401:
                yield ProviderStreamEvent(type="error", error="Invalid OLLAMA_API_KEY")
            elif e.status_code == 404:
                yield ProviderStreamEvent(type="error", error=f"Model '{config.model}' not available")
            elif e.status_code == 429:
                yield ProviderStreamEvent(type="error", error="Rate limit exceeded")
            else:
                yield ProviderStreamEvent(type="error", error=f"API error: {str(e)}")
        except Exception as e:
            yield ProviderStreamEvent(type="error", error=str(e))

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "ollama"

    def _build_ollama_messages(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str
    ) -> List[Dict[str, Any]]:
        """
        Build Ollama-compatible messages from OpenAI format.

        Args:
            messages: OpenAI-format messages
            system_prompt: System instructions

        Returns:
            Ollama-compatible messages list
        """
        # Prepend system prompt as first message
        ollama_messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Convert messages
        for msg in messages:
            if msg["role"] == "tool":
                # Convert OpenAI tool result format to Ollama format
                # OpenAI: {"role": "tool", "tool_call_id": "...", "name": "func", "content": "..."}
                # Ollama: {"role": "tool", "content": "...", "tool_name": "func"}
                ollama_messages.append({
                    "role": "tool",
                    "content": msg.get("content", ""),
                    "tool_name": msg.get("name", "")
                })
            else:
                # Other messages pass through
                ollama_messages.append(msg)

        return ollama_messages

    def _build_ollama_options(self, config: 'AgentConfig') -> Optional[Options]:
        """
        Build Ollama Options from AgentConfig.

        Args:
            config: Agent configuration

        Returns:
            Ollama Options object or None
        """
        # Map AgentConfig parameters to Ollama options
        options_dict = {}

        if config.temperature is not None:
            options_dict["temperature"] = config.temperature

        if config.top_p is not None:
            options_dict["top_p"] = config.top_p

        if config.max_tokens is not None:
            options_dict["num_predict"] = config.max_tokens

        if config.frequency_penalty is not None:
            options_dict["frequency_penalty"] = config.frequency_penalty

        if config.presence_penalty is not None:
            options_dict["presence_penalty"] = config.presence_penalty

        # Return Options object if any options were set
        if options_dict:
            return Options(**options_dict)

        return None

    def _normalize_response(self, response) -> ProviderResponse:
        """
        Normalize Ollama response to ProviderResponse format.

        Args:
            response: Raw Ollama API response (ChatResponse)

        Returns:
            Normalized ProviderResponse
        """
        # Extract content
        content = response.message.content if response.message.content else None

        # Extract tool calls if present
        tool_calls = None
        if response.message.tool_calls:
            tool_calls = []
            for tc in response.message.tool_calls:
                # Parse arguments if it's a JSON string
                arguments = tc.function.arguments
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)

                tool_calls.append(ToolCall(
                    id=self._generate_tool_call_id(tc.function.name, arguments),
                    name=tc.function.name,
                    arguments=arguments
                ))

        # Normalize finish reason - if we have tool calls, finish_reason should be "tool_calls"
        if tool_calls:
            finish_reason = "tool_calls"
        else:
            finish_reason = self._normalize_finish_reason(
                response.done_reason if hasattr(response, 'done_reason') else None
            )

        return ProviderResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            raw_response=response
        )

    def _normalize_finish_reason(self, done_reason: Optional[str]) -> str:
        """
        Normalize Ollama's done_reason to standard finish_reason.

        Args:
            done_reason: Ollama's done_reason value

        Returns:
            Normalized finish_reason ('stop', 'tool_calls', 'length')
        """
        if not done_reason:
            return "stop"

        # Map Ollama finish reasons to standard format
        if done_reason == "stop":
            return "stop"
        elif done_reason == "length":
            return "length"
        elif done_reason == "tool" or done_reason == "tool_calls":
            return "tool_calls"
        else:
            return "stop"  # Default

    def _generate_tool_call_id(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """
        Generate a deterministic tool call ID.

        Ollama doesn't provide tool call IDs, so we generate them
        based on function name and arguments.

        Args:
            function_name: Name of the function
            arguments: Function arguments

        Returns:
            Generated tool call ID
        """
        # Create a deterministic hash from name and arguments
        content = f"{function_name}_{json.dumps(arguments, sort_keys=True)}"
        hash_obj = hashlib.md5(content.encode())
        return f"call_{hash_obj.hexdigest()[:16]}"
