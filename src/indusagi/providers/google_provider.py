"""
Google Gemini provider implementation.

Handles API calls to Google's Gemini models via the Google GenAI SDK.
Supports both the Gemini Developer API and Vertex AI Gemini.
"""

import json
from typing import List, Dict, Any, Optional, Iterator, Tuple

from google import genai

from .base import BaseProvider, ProviderResponse, ToolCall, ProviderStreamEvent


class GoogleProvider(BaseProvider):
    """
    Google Gemini API provider implementation.

    Supports:
    - Gemini Developer API (api_key)
    - Vertex AI Gemini (vertexai=True + project/location)
    """

    def __init__(
        self,
        api_key: Optional[str],
        base_url: Optional[str] = None,
        use_vertexai: bool = False,
        project: Optional[str] = None,
        location: Optional[str] = None,
    ):
        """
        Initialize Google Gemini provider.

        Args:
            api_key: Google AI Studio (Gemini Developer API) key
            base_url: Optional custom API endpoint (if supported by SDK)
            use_vertexai: Enable Vertex AI lane
            project: GCP project ID for Vertex AI
            location: GCP location for Vertex AI

        Raises:
            ValueError: If no credentials are provided
        """
        if not api_key and not use_vertexai:
            raise ValueError(
                "GEMINI_API_KEY or GOOGLE_API_KEY is required for the Gemini Developer API. "
                "For Vertex AI, set GOOGLE_GENAI_USE_VERTEXAI=1 with GOOGLE_CLOUD_PROJECT "
                "and GOOGLE_CLOUD_LOCATION."
            )

        client_args: Dict[str, Any] = {}
        if api_key:
            client_args["api_key"] = api_key
        if use_vertexai:
            client_args["vertexai"] = True
            if project:
                client_args["project"] = project
            if location:
                client_args["location"] = location
        if base_url:
            client_args["http_options"] = {"base_url": base_url}

        self.client = genai.Client(**client_args)

    def create_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: "AgentConfig",
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> ProviderResponse:
        """
        Create a completion using Google's Gemini API.

        Args:
            messages: Conversation messages in OpenAI format
            system_prompt: System instructions
            config: Agent configuration
            tools: Optional tool schemas in OpenAI format

        Returns:
            Normalized ProviderResponse
        """
        contents = self._convert_messages_to_google(messages)
        tool_payload = self._convert_openai_tools(tools)

        api_params = self._build_api_params(
            contents=contents,
            system_prompt=system_prompt,
            config=config,
            tool_payload=tool_payload,
            include_system_instruction=True,
        )

        response = self._invoke_generate(
            self.client.models.generate_content,
            api_params,
            system_prompt,
        )

        return self._normalize_response(response)

    def create_streaming_completion(
        self,
        messages: List[Dict[str, Any]],
        system_prompt: str,
        config: "AgentConfig",
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Iterator[ProviderStreamEvent]:
        """
        Create a streaming completion using Google's Gemini API.

        Args:
            messages: Conversation messages in OpenAI format
            system_prompt: System instructions
            config: Agent configuration
            tools: Optional tool schemas in OpenAI format

        Yields:
            ProviderStreamEvent objects
        """
        contents = self._convert_messages_to_google(messages)
        tool_payload = self._convert_openai_tools(tools)

        api_params = self._build_api_params(
            contents=contents,
            system_prompt=system_prompt,
            config=config,
            tool_payload=tool_payload,
            include_system_instruction=True,
        )

        stream = self._invoke_generate(
            self.client.models.generate_content_stream,
            api_params,
            system_prompt,
        )

        saw_tool_call = False
        for chunk in stream:
            text = self._extract_text(chunk)
            if text:
                yield ProviderStreamEvent(type="content", content=text)

            for tool_call in self._extract_tool_calls(chunk):
                saw_tool_call = True
                yield ProviderStreamEvent(type="tool_call", tool_call=tool_call)

            finish_reason = self._extract_finish_reason(chunk)
            if finish_reason:
                if saw_tool_call:
                    finish_reason = "tool_calls"
                yield ProviderStreamEvent(type="done", finish_reason=finish_reason)

    def get_provider_name(self) -> str:
        """Get provider name."""
        return "google"

    def _build_api_params(
        self,
        contents: List[Dict[str, Any]],
        system_prompt: str,
        config: "AgentConfig",
        tool_payload: Optional[List[Dict[str, Any]]],
        include_system_instruction: bool,
    ) -> Dict[str, Any]:
        config_payload = {
            "temperature": config.temperature,
            "top_p": config.top_p,
            "max_output_tokens": config.max_tokens,
        }
        if include_system_instruction and system_prompt:
            config_payload["system_instruction"] = system_prompt
        if tool_payload:
            config_payload["tools"] = tool_payload

        api_params: Dict[str, Any] = {
            "model": config.model,
            "contents": contents,
            "config": {k: v for k, v in config_payload.items() if v is not None},
        }
        return api_params

    def _invoke_generate(
        self,
        method,
        api_params: Dict[str, Any],
        system_prompt: str,
    ):
        params = dict(api_params)
        attempts = 0
        last_exc: Optional[TypeError] = None

        while attempts < 4:
            try:
                return method(**params)
            except TypeError as exc:
                last_exc = exc
                message = str(exc)
                handled = False

                if "config" in message and "config" in params:
                    config_dict = self._ensure_config_dict(params.pop("config"))
                    system_value = config_dict.pop("system_instruction", None)
                    tools_value = config_dict.pop("tools", None)
                    if config_dict:
                        params["generation_config"] = config_dict
                    if system_value:
                        params["system_instruction"] = system_value
                    if tools_value:
                        params["tools"] = tools_value
                    handled = True

                if "generation_config" in message and "generation_config" in params:
                    generation_config = params.pop("generation_config", None)
                    if generation_config is not None:
                        config_dict = self._ensure_config_dict(params.get("config"))
                        if isinstance(generation_config, dict):
                            config_dict.update(generation_config)
                        params["config"] = config_dict
                    handled = True

                if "system_instruction" in message and "system_instruction" in params:
                    system_value = params.pop("system_instruction", None)
                    if system_value:
                        params["contents"] = self._prepend_system_prompt(
                            params.get("contents", []), system_value
                        )
                    handled = True

                if "tools" in message and "tools" in params:
                    tools_value = params.pop("tools", None)
                    if tools_value:
                        config_dict = self._ensure_config_dict(params.get("config"))
                        config_dict["tools"] = tools_value
                        params["config"] = config_dict
                    handled = True

                if not handled:
                    raise

                attempts += 1

        if last_exc is not None:
            raise last_exc
        raise TypeError("Failed to call Gemini API with the provided parameters.")

    def _ensure_config_dict(self, config_value: Any) -> Dict[str, Any]:
        if config_value is None:
            return {}
        if isinstance(config_value, dict):
            return dict(config_value)
        model_dump = getattr(config_value, "model_dump", None)
        if callable(model_dump):
            return dict(model_dump())
        to_dict = getattr(config_value, "to_dict", None)
        if callable(to_dict):
            return dict(to_dict())
        return dict(getattr(config_value, "__dict__", {}))

    def _prepend_system_prompt(
        self, contents: List[Dict[str, Any]], system_prompt: str
    ) -> List[Dict[str, Any]]:
        if not system_prompt:
            return contents
        system_content = {"role": "user", "parts": [{"text": system_prompt}]}
        return [system_content] + list(contents)

    def _convert_openai_tools(
        self, tools: Optional[List[Dict[str, Any]]]
    ) -> Optional[List[Dict[str, Any]]]:
        if not tools:
            return None

        function_declarations = []
        for tool in tools:
            if tool.get("type") != "function":
                continue
            func = tool.get("function", {})
            function_declarations.append(
                {
                    "name": func.get("name", ""),
                    "description": func.get("description", ""),
                    "parameters": func.get("parameters", {}),
                }
            )

        if not function_declarations:
            return None

        return [{"function_declarations": function_declarations}]

    def _convert_messages_to_google(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        contents: List[Dict[str, Any]] = []
        tool_call_name_by_id = self._collect_tool_call_names(messages)

        for msg in messages:
            role = msg.get("role")

            if role == "assistant":
                parts: List[Dict[str, Any]] = []
                if msg.get("content"):
                    parts.append({"text": msg["content"]})

                for tool_call in msg.get("tool_calls", []) or []:
                    function_call, thought_signature = self._convert_tool_call_to_google(tool_call)
                    if function_call:
                        part = {"function_call": function_call}
                        if thought_signature is not None:
                            part["thought_signature"] = thought_signature
                        parts.append(part)

                if parts:
                    contents.append({"role": "model", "parts": parts})

            elif role == "tool":
                tool_name = tool_call_name_by_id.get(msg.get("tool_call_id"), "tool")
                contents.append(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "function_response": {
                                    "name": tool_name,
                                    "response": {"content": msg.get("content", "")},
                                }
                            }
                        ],
                    }
                )

            else:
                contents.append(
                    {"role": "user", "parts": [{"text": msg.get("content", "")}]}
                )

        return contents

    def _collect_tool_call_names(self, messages: List[Dict[str, Any]]) -> Dict[str, str]:
        tool_call_name_by_id: Dict[str, str] = {}
        for msg in messages:
            if msg.get("role") == "assistant" and msg.get("tool_calls"):
                for tool_call in msg.get("tool_calls", []) or []:
                    tool_call_id = tool_call.get("id")
                    function = tool_call.get("function", {})
                    name = function.get("name")
                    if tool_call_id and name:
                        tool_call_name_by_id[tool_call_id] = name
        return tool_call_name_by_id

    def _convert_tool_call_to_google(
        self, tool_call: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Any]]:
        function = tool_call.get("function", {})
        name = function.get("name")
        arguments = function.get("arguments", "")
        thought_signature = tool_call.get("thought_signature")
        if not name:
            return None, thought_signature

        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments) if arguments else {}
            except json.JSONDecodeError:
                arguments = {}

        return {"name": name, "args": arguments}, thought_signature

    def _normalize_response(self, response) -> ProviderResponse:
        content = self._extract_text(response)
        tool_calls = self._extract_tool_calls(response)
        finish_reason = self._extract_finish_reason(response)

        if tool_calls:
            finish_reason = "tool_calls"
        if not finish_reason:
            finish_reason = "stop"

        return ProviderResponse(
            content=content,
            tool_calls=tool_calls or None,
            finish_reason=finish_reason,
            raw_response=response,
        )

    def _extract_text(self, response) -> Optional[str]:
        text = getattr(response, "text", None)
        if text:
            return text

        candidates = getattr(response, "candidates", None)
        if not candidates:
            return None

        content = getattr(candidates[0], "content", None)
        parts = getattr(content, "parts", None) if content else None
        if not parts:
            return None

        collected = []
        for part in parts:
            part_text = getattr(part, "text", None)
            if part_text:
                collected.append(part_text)
        return "".join(collected) if collected else None

    def _extract_tool_calls(self, response) -> List[ToolCall]:
        tool_calls: List[ToolCall] = []
        candidates = getattr(response, "candidates", None)
        if not candidates:
            return tool_calls

        content = getattr(candidates[0], "content", None)
        parts = getattr(content, "parts", None) if content else None
        if not parts:
            return tool_calls

        for part in parts:
            function_call = getattr(part, "function_call", None)
            if function_call is None and isinstance(part, dict):
                function_call = part.get("function_call")
            if not function_call:
                continue
            thought_signature = getattr(part, "thought_signature", None)
            if thought_signature is None and isinstance(part, dict):
                thought_signature = part.get("thought_signature")

            name = getattr(function_call, "name", None)
            args = getattr(function_call, "args", None)
            if name is None and isinstance(function_call, dict):
                name = function_call.get("name")
            if args is None and isinstance(function_call, dict):
                args = function_call.get("args", {})

            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {}

            tool_calls.append(
                ToolCall(
                    id=f"{name or 'tool'}-{len(tool_calls) + 1}",
                    name=name or "tool",
                    arguments=args or {},
                    thought_signature=thought_signature,
                )
            )

        return tool_calls

    def _extract_finish_reason(self, response) -> Optional[str]:
        candidates = getattr(response, "candidates", None)
        if not candidates:
            return None

        return getattr(candidates[0], "finish_reason", None)
