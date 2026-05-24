"""
Visualization type thing.
Correlation. Graphs Only I guess
"""

from typing import Literal
from pydantic import BaseModel
from .context import DataFrameContext
from .agent import Agent
import json
import pandas as pd
import numpy as np


# Modelssssss
class Chart(BaseModel):
    chart_title: str
    chart_type: Literal["bar", "scatter", "line"]
    x_col: str
    y_col: str


class Piechart(BaseModel):
    chart_title: str
    column: str


def generate_pie_chart_data(df_context: DataFrameContext, column: str, limit: int = 10):
    """Generate pie chart data from a dataframe column.

    Args:
        df_context (DataFrameContext): The dataframe context
        column (str): The column to create pie chart from
        limit (int): Maximum number of slices to show (others grouped as 'Other'). Defaults to 10.

    Returns:
        dict: Dictionary with labels and values for pie chart
    """
    df = df_context.dataframe

    # Handle numeric and categorical columns
    if df[column].dtype in ["int64", "float64"]:
        # For numeric columns, use value counts or bins
        value_counts = df[column].value_counts(bins=limit).head(limit)
    else:
        # For categorical columns, get top values
        value_counts = df[column].value_counts().head(limit)

    # Group smaller slices as 'Other'
    labels = list(value_counts.index.astype(str))
    values = list(value_counts.values)

    # If there are more values beyond the limit, group them
    total_all = df[column].value_counts().sum()
    total_shown = value_counts.sum()

    if total_shown < total_all:
        labels.append("Other")
        values.append(total_all - total_shown)

    return {"labels": labels, "values": values, "total": total_all}


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


# encoder flani
class NumPyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        if isinstance(obj, (np.float64, np.float32, np.float16)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


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

    def _run(
        self,
        query=None,
        model=None,
        stream=False,
        context: DataFrameContext | None = None,
    ):
        if context:
            self.context = context
        elif self.context is None:
            raise Exception("Empty context")
        chart_responses = []
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
                self.summary = response.choices[0].message.content
                break
            elif response.choices[0].finish_reason == "tool_calls":
                print(response.choices[0])

                for _tool in response.choices[0].message.tool_calls:
                    # Call each tool and add the values back to the loop for continuation
                    try:
                        args = json.loads(_tool.function.arguments)
                        if _tool.function.name == "create_chart":
                            tool_response = create_chart(**args)

                            # Handle both Pydantic models and dicts
                            if hasattr(tool_response, "model_dump_json"):
                                chart_json = tool_response.model_dump_json()
                                chart_obj = tool_response.model_dump()
                            else:
                                chart_json = json.dumps(tool_response)
                                chart_obj = tool_response

                            self.history.append(
                                {
                                    "role": "tool",
                                    "content": str(tool_response),
                                    "tool_name": "create_chart",
                                }
                            )
                            chart_responses.append(chart_obj)
                            # yield chart_json
                        else:
                            self._run_tool(
                                tool_name=_tool.function.name,
                                model_args=args,
                            )

                    except Exception as e:
                        print(f"Error executing tool {_tool.function.name}: {e}")
                        # Optionally append an error message to history to let the LLM retry
                        self.history.append(
                            {
                                "role": "tool",
                                "content": f"Error: {str(e)}",
                                "tool_name": _tool.function.name,
                            }
                        )
        charts = self.generate_charts_for_frontend(chart_responses)
        return [json.dumps(chart, cls=NumPyEncoder) for chart in charts]

    def generate_charts_for_frontend(self, results):
        charts = []
        for r in results:
            df = self.context.dataframe
            try:
                # Check if r is already a dict, if not, parse it
                if isinstance(r, str):
                    chart_data = json.loads(r)
                else:
                    chart_data = r

                # Determine chart type from the object's structure
                # If it's a Piechart (has 'column' key), handle it
                if "column" in chart_data:
                    chart_type = "pie"
                    # Get the column name
                    pie_column = chart_data["column"]
                    # Generate pie chart data
                    pie_data = generate_pie_chart_data(self.context, pie_column)
                    chart_config = {
                        "id": f"chart_{pie_column}_pie",
                        "type": "pie",
                        "title": chart_data["chart_title"],
                        "labels": pie_data["labels"],
                        "datasets": [
                            {
                                "label": pie_column,
                                "data": pie_data["values"],
                                "backgroundColor": [
                                    "rgba(255, 99, 132, 0.8)",
                                    "rgba(54, 162, 235, 0.8)",
                                    "rgba(255, 206, 86, 0.8)",
                                    "rgba(75, 192, 192, 0.8)",
                                    "rgba(153, 102, 255, 0.8)",
                                    "rgba(255, 159, 64, 0.8)",
                                    "rgba(199, 199, 199, 0.8)",
                                ],
                                "borderColor": [
                                    "rgb(255, 99, 132)",
                                    "rgb(54, 162, 235)",
                                    "rgb(255, 206, 86)",
                                    "rgb(75, 192, 192)",
                                    "rgb(153, 102, 255)",
                                    "rgb(255, 159, 64)",
                                    "rgb(199, 199, 199)",
                                ],
                                "borderWidth": 2,
                            }
                        ],
                    }
                    charts.append(chart_config)

                # If it's a Chart (has 'x_col' and 'y_col'), handle it
                elif "x_col" in chart_data and "y_col" in chart_data:
                    chart_type = (
                        chart_data.get("chart_type") or "scatter"
                    )  # Default to scatter if missing

                    # Ensure columns exist
                    if (
                        chart_data["x_col"] not in df.columns
                        or chart_data["y_col"] not in df.columns
                    ):
                        print(
                            f"Warning: Columns {chart_data['x_col']} or {chart_data['y_col']} not found. Skipping."
                        )
                        continue

                    clean_df = df.dropna(
                        subset=[chart_data["x_col"], chart_data["y_col"]]
                    )

                    if chart_type == "line" or chart_type == "bar":
                        if chart_type == "line":
                            data = (
                                clean_df.groupby(chart_data["x_col"])[
                                    chart_data["y_col"]
                                ]
                                .mean()
                                .sort_index()
                                .to_dict()
                            )
                        else:
                            data = (
                                clean_df.groupby(chart_data["x_col"])[
                                    chart_data["y_col"]
                                ]
                                .mean()
                                .sort_values(ascending=False)
                                .to_dict()
                            )

                        labels = list(data.keys())
                        values = [float(v) for v in data.values()]

                        chart_config = {
                            "id": f"chart_{chart_data['x_col']}_{chart_data['y_col']}",
                            "type": chart_type,
                            "title": chart_data["chart_title"],
                            "labels": labels,
                            "datasets": [
                                {
                                    "label": chart_data["y_col"],
                                    "data": values,
                                    "borderColor": "#36a2eb",
                                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                                    "fill": chart_type == "line",
                                    "tension": 0.4,
                                }
                            ],
                        }
                        charts.append(chart_config)

                    elif chart_type == "scatter":
                        corr = clean_df[chart_data["x_col"]].corr(
                            clean_df[chart_data["y_col"]]
                        )
                        # Convert dataframe to list of dicts for scatter points
                        # Convert numpy types to native Python types
                        points_data = clean_df.apply(
                            lambda row: {
                                "x": (
                                    float(row[chart_data["x_col"]])
                                    if not pd.isna(row[chart_data["x_col"]])
                                    else None
                                ),
                                "y": (
                                    float(row[chart_data["y_col"]])
                                    if not pd.isna(row[chart_data["y_col"]])
                                    else None
                                ),
                            },
                            axis=1,
                        ).tolist()

                        # Remove any points that have None (if you want to clean them)
                        # points_data = [p for p in points_data if p['x'] is not None and p['y'] is not None]

                        chart_config = {
                            "id": f"chart_{chart_data['x_col']}_{chart_data['y_col']}",
                            "type": "scatter",
                            "title": chart_data["chart_title"],
                            "datasets": [
                                {
                                    "label": "Data Points",
                                    "data": points_data,
                                    "backgroundColor": "rgba(255, 99, 132, 0.5)",
                                }
                            ],
                            "correlation_coefficient": float(
                                corr
                            ),  # Convert numpy float to Python float
                        }
                        charts.append(chart_config)

                else:
                    # If it's neither pie nor chart, skip
                    print(f"Warning: Skipping unrecognized chart data: {chart_data}")
                    continue

            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error processing chart response {r}: {e}")
                continue

        return charts
