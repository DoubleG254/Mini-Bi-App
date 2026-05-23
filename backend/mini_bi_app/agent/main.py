from .agent import Agent
from dotenv import load_dotenv
import os
import json
from mini_bi_app.models import Report
from .data_cleaning import *
from .prompts import visualization_prompt, cleaning_prompt
from .data_visualization import *

load_dotenv()
def main(dataset_path, dataset_instance=None,user=None):
    cleaner = Agent(
        base_url="https://ollama.com/v1",
        api_key=os.getenv("OLLAMA_API_KEY"),
        model="ministral-3:8b-cloud",
        system_prompt=cleaning_prompt(),
        dataframe_context=DataFrameContext(dataset_path),
        tools= [
            drop_row,
            drop_column,
            get_dataset_head,
            save_dataset,
            get_all_columns,
            get_dataset_description,
            get_null_values,
            fetch_column,
            fill_null_values,
        ],
    )
    cleaner.run()
 # Fallback to original dataset if no cleaned file is produced
    # print(f"Dataset saved at: {file_path}")
    
    # cleaning_agent = VisualizationAgent(
    #     base_url="https://ollama.com/v1",
    #     api_key=os.getenv("OLLAMA_API_KEY"),
    #     model="ministral-3:8b-cloud",
    #     system_prompt=visualization_prompt(),
    #     dataframe_context=DataFrameContext(file_path),
    #     tools=[
    #         get_dataset_head,
    #         get_all_columns,
    #         get_dataset_description,
    #         compare_correlation,
    #         whole_dataset_correlation,
    #         create_chart,
    #     ],
    # )
    # charts_list = []
    # for item in cleaning_agent.run():
    #     try:
    #         # If item is already a dict (from model_dump), skip parsing
    #         if isinstance(item, dict):
    #             charts_list.append(item)
    #         else:
    #             charts_list.append(json.loads(item))
    #     except (json.JSONDecodeError, TypeError) as e:
    #         print(f"Skipping invalid item: {e}")
    #         continue

    # report = Report.objects.create(
    #     dataset=dataset_instance,
    #     user=user,
    #     summary={},
    #     charts=charts_list
    # )
    # return report
# if __name__ == "__main__":

#     # def problem(a, b):
#     #     """Calculate the problem ie the product of two values

#     #     Args:
#     #         a (int): The first value
#     #         b (int): The second value

#     #     Returns:
#     #         str: The problem between the two values
#     #     """
#     #     return str(a * b)

#     # def weather(location: str):
#     #     return str({"temperature": "60 degree celsius", "raining": False})

#     # agent = Agent(
#     #     base_url="https://ollama.com/v1",
#     #     api_key=os.getenv("OLLAMA_API_KEY"),
#     #     system_prompt="use the problem tool with a and b as arguments to find the problem between given values, use the 'weather' tool to find the weather in different locations by passing the locations",
#     #     model="gpt-oss:120b-cloud",
#     #     tools=[problem, weather],
#     # )

#     # @agent.tool
#     # def weather(location: str):
#     #     return str({"temperature": "60 degree celsius", "raining": False})

#     # agent.run("What is the temperature in Nairobi")
#     # # print(agent.add_tools_to_system_prompt("someone"))

  

#          # Construct the file path relative to this script's location
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     # Navigate up 2 levels to reach the backend directory (ai_pipeline -> mini_bi_app -> backend)
#     backend_dir = os.path.dirname(os.path.dirname(script_dir))
#     data_dir = os.path.dirname(backend_dir)
#     test_data_dir = os.path.join(data_dir,"media","datasets","finance.csv")
#     print(test_data_dir)
#     cleaner = Agent(
#         base_url="https://ollama.com/v1",
#         api_key=os.getenv("OLLAMA_API_KEY"),
#         model="ministral-3:8b-cloud",
#         system_prompt=cleaning_prompt(),
#         dataframe_context=DataFrameContext(test_data_dir),
#         tools= [
#             drop_row,
#             drop_column,
#             get_dataset_head,
#             save_dataset,
#             get_all_columns,
#             get_dataset_description,
#             get_null_values,
#             fetch_column,
#             fill_null_values,
#         ],
#     )
#     file_path = "/home/g-cubed/Documents/BSE_Y3S2/Project/MINI_BI/Mini-Bi-App/backend/media/cleaned_datasets/cleaned_alabama_financial_data.csv"
#     print(f"Dataset saved at: {file_path}")

#     cleaning_agent = VisualizationAgent(
#         base_url="https://ollama.com/v1",
#         api_key=os.getenv("OLLAMA_API_KEY"),
#         model="ministral-3:8b-cloud",
#         system_prompt=visualization_prompt(),
#         dataframe_context=DataFrameContext(file_path),
#         tools=[
#             get_dataset_head,
#             get_all_columns,
#             get_dataset_description,
#             compare_correlation,
#             whole_dataset_correlation,
#             create_chart,
#         ],
#     )
#     graphs = cleaning_agent.run()
#     for graph in graphs:
#         chart_data = json.loads(graph)
#         print(chart_data)
   
   