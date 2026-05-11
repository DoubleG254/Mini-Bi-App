from openai import OpenAI
from typing import Iterable, Callable, Optional
import json
from .context import DataFrameContext
import inspect


class Agent:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str | None = "gpt-oss",
        tools: list[Callable] | None = None,
        system_prompt: str | None = None,
        message_history: list | None = None,
        dataframe_context: DataFrameContext | None = None,
    ):
        self._openai: OpenAI = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.tools = self._define_tool_dictionary(tools) if tools else {}
        self.system_prompt = system_prompt
        self.history = [{}]
        self._update_system_prompt()
        if message_history:
            self.history += message_history

        self.context = dataframe_context

    def _update_system_prompt(self):
        self.history[0] = {
            "role": "system",
            "content": (
                self._add_tools_to_system_prompt(self.system_prompt)
                if self.system_prompt
                else "You are a helpful assistant"
            ),
        }

    def _define_tool_dictionary(self, tools: list[callable]) -> list[dict]:
        return {
            tool.__name__: {"callable": tool, "docs": tool.__doc__} for tool in tools
        }

    def _add_tools_to_system_prompt(self, system_prompt: str):
        if len(self.tools) > 0:
            return (
                system_prompt
                + f"\nThe tools at your disposal are: {self._stringify_tools()}"
            )
        else:
            return system_prompt

    def _stringify_tools(self):
        tools_string = ""
        for idx, tool in enumerate(self.tools):
            tools_string += f"\n{idx + 1}.{tool} \n DESC: \n {self.tools[tool]["docs"]}"

        return tools_string

    def _get_openai_tools_schema(self) -> list[dict]:
        """Convert tool functions to OpenAI function schema format.
        
        Returns:
            list[dict]: List of tool schemas compatible with OpenAI API
        """
        openai_tools = []
        for tool_name, tool_info in self.tools.items():
            func = tool_info["callable"]
            sig = inspect.signature(func)
            
            # Build parameters schema
            properties = {}
            required = []
            
            for param_name, param in sig.parameters.items():
                # Skip DataFrameContext parameters - these are injected by _run_tool
                if param.annotation is DataFrameContext:
                    continue
                    
                param_type = "string"  # default
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation in (list, list[str]):
                    param_type = "array"
                
                properties[param_name] = {
                    "type": param_type,
                    "description": f"Parameter: {param_name}"
                }
                
                # All parameters without defaults are required
                if param.default is inspect.Parameter.empty:
                    required.append(param_name)
            
            tool_schema = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_info["docs"] or f"Call the {tool_name} function",
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            }
            openai_tools.append(tool_schema)
        
        return openai_tools

    def tool(self, func):
        """The @Agent.tool decorator for tools

        Args:
            func (Callable): The tool function

        Returns:
            Callable: The function passed
        """
        self.tools[func.__name__] = {"callable": func, "docs": func.__doc__}
        # TODO: Update the System prompt to contain this tool -> Nashuku this works
        self._update_system_prompt()
        return func

    def _run_tool(self, tool_name: str, model_args: dict):
        tool_found = self.tools.get(tool_name)
        if tool_found:
            tool_signature = inspect.signature(tool_found["callable"])

            for param_name, param in tool_signature.parameters.items():
                if param.annotation is DataFrameContext:
                    model_args[param_name] = self.context
                    break
            try:
                tool_response = tool_found["callable"](**model_args)
                
                # Serialize the response to a JSON string
                if tool_response is None:
                    content_str = "Operation complete"
                elif hasattr(tool_response, 'model_dump_json'):
                    # If it's a Pydantic model, use its JSON method
                    content_str = tool_response.model_dump_json()
                elif isinstance(tool_response, dict):
                    # If it's a dict, convert to JSON string
                    content_str = json.dumps(tool_response)
                else:
                    # Fallback for strings or other types
                    content_str = str(tool_response)

                self.history.append(
                    {
                        "role": "tool",
                        "content": content_str,  # Now it's a guaranteed JSON string
                        "tool_name": tool_name,
                        # Optional: Add tool_call_id if your API requires it
                        # "tool_call_id": tool_call_id 
                    }
                )
                return tool_response
            except Exception as e:
                self.history.append(
                    {
                        "role": "tool",
                        "content": f"Error: {e}",
                        "tool_name": tool_name,
                    }
                )
        else:
            self.history.append(
                {
                    "role": "tool",
                    "content": "ERROR: Tool not found check tool name and try again",
                    "tool_name": tool_name,
                }
            )

    def run(
        self, query: str | None = None, model: str | None = None, stream: bool = False
    ):
        # self.history.append({"role": "user", "content": query})
        last_result = None
        while True:
            response = self._openai.chat.completions.create(
                model=model if model else self.model,
                messages=self.history,
                tool_choice="required",
                tools=self._get_openai_tools_schema() if self.tools else None,
            )
            self.history.append(response.choices[0].message)
            if response.choices[0].finish_reason == "stop":
                # When the loop is complete
                print(response.choices[0].message)
                break
            elif response.choices[0].finish_reason == "tool_calls":
                print(response.choices[0])
                for _tool in response.choices[0].message.tool_calls:
                    # Call each tool and add the values back to the loop for continuation
                    last_result = self._run_tool(
                        tool_name=_tool.function.name,
                        model_args=json.loads(_tool.function.arguments),
                    )
                    

            else:
                print("Will be handled later!!!")
        return last_result