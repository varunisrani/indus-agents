"""
Groq provider implementation.

Handles API calls to Groq's fast inference API.
Groq is OpenAI-compatible, so the implementation is similar to OpenAI provider.
"""

import json
from typing import List, Dict, Any, Optional, Iterator
from groq import Groq
from .base import BaseProvider, ProviderResponse, ToolCall, ProviderStreamEvent


class GroqProvider(BaseProvider):
    """
    Groq API provider implementation.

    Handles communication with Groq's fast inference API using the official Python SDK.
    Groq is OpenAI-compatible and known for extremely fast inference.
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize Groq provider.

        Args:
            api_key: Groq API key
            base_url: Optional custom API endpoint (usually not needed)

        Raises:
            ValueError: If api_key is not provided
        """
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is required. "
                "Please set it with: export GROQ_API_KEY='your-key-here'"
            )

        if base_url:
            self.client = Groq(api_key=api_key, base_url=base_url)
        else:
            self.client = Groq(api_key=api_key)

    def create_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: 'AgentConfig',
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> ProviderResponse:
        """
        Create a completion using Groq's API.

        Args:
            messages: Conversation messages in OpenAI format
            system_prompt: System instructions
            config: Agent configuration
            tools: Optional tool schemas

        Returns:
            Normalized ProviderResponse

        Raises:
            Exception: If API call fails
        """
        # Build OpenAI-style messages with system prompt
        api_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

        # Build API parameters
        api_params = {
            "model": config.model,
            "messages": api_messages,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
        }

        # Add top_p if specified
        if config.top_p is not None:
            api_params["top_p"] = config.top_p

        # Add tools if provided
        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = "auto"

        # Call Groq API
        response = self.client.chat.completions.create(**api_params)

        # Normalize response
        return self._normalize_response(response)

    def create_streaming_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: 'AgentConfig',
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Iterator[ProviderStreamEvent]:
        """
        Create a streaming completion using Groq's API.

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
        # Build messages
        api_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

        # Build API parameters
        api_params = {
            "model": config.model,
            "messages": api_messages,
            "stream": True,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
        }

        if config.top_p is not None:
            api_params["top_p"] = config.top_p

        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = "auto"

        # Stream response
        stream = self.client.chat.completions.create(**api_params)

        # Track tool calls across chunks (Groq streams tool calls in parts)
        accumulated_tool_calls = {}

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            # Yield content deltas
            if delta.content:
                yield ProviderStreamEvent(
                    type="content",
                    content=delta.content
                )

            # Accumulate tool calls
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in accumulated_tool_calls:
                        accumulated_tool_calls[idx] = {
                            "id": tc.id or "",
                            "name": "",
                            "arguments": ""
                        }

                    if tc.id:
                        accumulated_tool_calls[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            accumulated_tool_calls[idx]["name"] = tc.function.name
                        if tc.function.arguments:
                            accumulated_tool_calls[idx]["arguments"] += tc.function.arguments

            # Check for finish
            if chunk.choices[0].finish_reason:
                finish_reason = chunk.choices[0].finish_reason

                # Yield accumulated tool calls
                if accumulated_tool_calls:
                    for idx, tc_data in accumulated_tool_calls.items():
                        try:
                            arguments = json.loads(tc_data["arguments"]) if tc_data["arguments"] else {}
                        except json.JSONDecodeError:
                            arguments = {}

                        yield ProviderStreamEvent(
                            type="tool_call",
                            tool_call=ToolCall(
                                id=tc_data["id"],
                                name=tc_data["name"],
                                arguments=arguments
                            )
                        )
                    finish_reason = "tool_calls"

                yield ProviderStreamEvent(
                    type="done",
                    finish_reason=finish_reason
                )

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "groq"

    def _normalize_response(self, response) -> ProviderResponse:
        """
        Normalize Groq response to ProviderResponse format.

        Args:
            response: Raw Groq API response

        Returns:
            Normalized ProviderResponse
        """
        response_message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # Extract content
        content = response_message.content

        # Extract tool calls if present
        tool_calls = None
        if response_message.tool_calls:
            tool_calls = []
            for tc in response_message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments) if tc.function.arguments else {}
                ))
            # Ensure finish_reason is "tool_calls" when we have tool calls
            finish_reason = "tool_calls"

        return ProviderResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            raw_response=response
        )
