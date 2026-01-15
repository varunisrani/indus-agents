"""
Mistral provider implementation.

Handles API calls to Mistral's OpenAI-compatible chat completions API.
"""

import json
from typing import List, Dict, Any, Optional, Iterator
from openai import OpenAI
from .base import BaseProvider, ProviderResponse, ToolCall, ProviderStreamEvent


class MistralProvider(BaseProvider):
    """
    Mistral API provider implementation.

    Uses the OpenAI SDK against Mistral's OpenAI-compatible endpoint.
    """

    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize Mistral provider.

        Args:
            api_key: Mistral API key
            base_url: Optional custom API endpoint

        Raises:
            ValueError: If api_key is not provided
        """
        if not api_key:
            raise ValueError(
                "MISTRAL_API_KEY is required. "
                "Please set it with: export MISTRAL_API_KEY='your-key-here'"
            )

        resolved_base_url = base_url or "https://api.mistral.ai/v1"
        self.client = OpenAI(api_key=api_key, base_url=resolved_base_url)

    def create_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: 'AgentConfig',
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> ProviderResponse:
        """
        Create a completion using Mistral's API.

        Args:
            messages: Conversation messages in OpenAI format
            system_prompt: System instructions
            config: Agent configuration
            tools: Optional tool schemas

        Returns:
            Normalized ProviderResponse
        """
        api_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

        api_params = {
            "model": config.model,
            "messages": api_messages,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
        }

        if config.top_p is not None:
            api_params["top_p"] = config.top_p

        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**api_params)
        return self._normalize_response(response)

    def create_streaming_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: 'AgentConfig',
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Iterator[ProviderStreamEvent]:
        """
        Create a streaming completion using Mistral's API.

        Args:
            messages: Conversation messages
            system_prompt: System instructions
            config: Agent configuration
            tools: Optional tool schemas

        Yields:
            ProviderStreamEvent objects
        """
        api_messages = [
            {"role": "system", "content": system_prompt},
            *messages
        ]

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

        stream = self.client.chat.completions.create(**api_params)

        accumulated_tool_calls: Dict[int, Dict[str, str]] = {}

        for chunk in stream:
            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            if delta.content:
                yield ProviderStreamEvent(
                    type="content",
                    content=delta.content
                )

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

            if chunk.choices[0].finish_reason:
                finish_reason = chunk.choices[0].finish_reason

                if accumulated_tool_calls:
                    for tc_data in accumulated_tool_calls.values():
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
        return "mistral"

    def _normalize_response(self, response) -> ProviderResponse:
        """
        Normalize Mistral response to ProviderResponse format.

        Args:
            response: Raw API response

        Returns:
            Normalized ProviderResponse
        """
        response_message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        content = response_message.content

        tool_calls = None
        if response_message.tool_calls:
            tool_calls = []
            for tc in response_message.tool_calls:
                try:
                    arguments = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=arguments
                ))

        return ProviderResponse(
            content=content,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            raw_response=response
        )
