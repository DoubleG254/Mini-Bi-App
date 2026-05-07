"""
Visualization type thing.
Correlation. Graphs Only I guess
"""

from typing import Literal
from pydantic import BaseModel
from .context import DataFrameContext
from .agent import Agent
import json


# Modelssssss
class Chart(BaseModel):
    chart_title: str
    chart_type: Literal["bar", "scatter", "line"]
    x_col: str
    y_col: str


class Piechart(BaseModel):
    chart_title: str
    column: str


def compare_correlation(
    df_context: DataFrameContext,
    first_column: str,
    second_column: str,
    method: Literal["pearson", "kendall", "spearman"] = "pearson",
) -> str:
    """Compare the correlation between two columns

    Args:
        first_column (str): The first column
        second_column (str): The second column
        method (Literal[&quot;pearson&quot;, &quot;kendall&quot;, &quot;spearman&quot;], optional): The correlation method to be used. Defaults to "pearson".

    Returns:
        str: _description_
    """
    return str(
        df_context.dataframe[first_column].corr(
            df_context.dataframe[second_column], method=method
        )
    )


def whole_dataset_correlation(
    df_context: DataFrameContext,
    method: Literal["pearson", "kendall", "spearman"] = "pearson",
) -> str:
    """Get the correlation of the whole dataset

    Args:
        method (Literal[&quot;pearson&quot;, &quot;kendall&quot;, &quot;spearman&quot;], optional): The correlation method to be used. Defaults to "pearson".


    Returns:
        str: A string representation of the correlation in the whole dataset
    """
    return df_context.dataframe.corr(method=method).to_string()


def create_chart(
    chart_type: Literal["bar", "scatter", "line", "pie"],
    chart_title: str,
    y_column: str | None = None,
    x_column: str | None = None,
    pie_column: str | None = None,
):
    """Creates a graph

    Args:
        chart_type (Literal[&quot;bar&quot;, &quot;scatter&quot;, &quot;line&quot;, &quot;pie&quot;]): _description_
        chart_title (str): _description_
        y_column (str | None, optional): The name of the column on the y-axis. Defaults to None.
        x_column (str | None, optional): The name of the column in the x-axis. Defaults to None.
        pie_column (str | None, optional): The name of the column if the graph is pie. Defaults to None.

    Returns:
        str: A str rep of what has been visualized
    """
    if chart_type == "pie":
        return Piechart(chart_title=chart_title, column=pie_column)
    else:
        return Chart(
            chart_title=chart_title,
            chart_type=chart_type,
            x_col=x_column,
            y_col=y_column,
        )


"""
NEEED TO RANT!!!!!

So I should maybe override the base agent to create a visualization agent. 
Need it to yield the graphs as we go.

"""


class VisualizationAgent(Agent):
    def __init__(
        self,
        base_url,
        api_key,
        model="gpt-oss",
        tools=None,
        system_prompt=None,
        message_history=None,
        dataframe_context=None,
    ):
        super().__init__(
            base_url,
            api_key,
            model,
            tools,
            system_prompt,
            message_history,
            dataframe_context,
        )

    def run(self, query=None, model=None, stream=False):
        while True:
            response = self._openai.chat.completions.create(
                model=model if model else self.model,
                messages=self.history,
                tool_choice="required",
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
                    if _tool.function.name == "create_chart":
                        tool_response = create_chart(
                            **json.loads(_tool.function.arguments)
                        )
                        self.history.append({
                            
                            "role": "tool",
                            "content": str(tool_response),
                            "tool_name": "create_chart",
                        
                        })
                        yield tool_response
                    else:
                        self._run_tool(
                            tool_name=_tool.function.name,
                            model_args=json.loads(_tool.function.arguments),
                        )
            else:
                print("Will be handled later!!!")
