
from langchain_core.messages import AIMessage, ToolMessage, ToolCall


PREDEFINED_REPLIES = [
    "I'm sorry, but I cannot assist with that."*100,
    "Can you please provide more details?",
    "I don't have the information you're looking for."
    ]

SEARCH_RESULT = {
    "query": "法国的首都是哪里",
    "images": [],
    "results": [
      {
        "title": "法国的首都是哪？ - 百度知道",
        "url": "https://zhidao.baidu.com/question/586329932.html",
        "content": "法国的首都是哪？法国首都巴黎（Paris）是欧洲大陆上最大的城市，也是世界上最繁华的都市之一。地处法国北部，塞纳河西岸，距河口（英吉利海峡）375公里。塞纳河蜿蜒穿过城市，形成两座河心岛（斯德和圣路易）。",
        "score": 0.91362286,
      },
      {
        "title": "法国的首都在哪? - 游仁新知网",
        "url": "https://www.lishixinzhi.com/cc/911460.html",
        "content": "法国的首都在哪里？ 巴黎是法国的首都和最大的城市，也是法国的政治、经济、文化中心，同时又是四大世界级城市之一，仅次于美国纽约、英国伦敦，和日本东京并列。 法国的首都是哪里 巴黎（Paris），是法兰西共和国的首都，法国最大城市，欧洲第二大城市，法国的政治、经济",
        "score": 0.8995547,
      }
    ],
    "response_time": 2.28
  }


TOOL_CALL_MESSAGE = AIMessage(
    content="\n\n根据我的知识，法国的首都是巴黎（Paris）。不过为了确认最新信息并确保准确性，我可以用工具为您查询一下最新的结果。以下是我使用工具进行搜索的步骤：\n\n",
    tool_calls=[ToolCall(name="search", args={"query": "法国的首都是哪里"}, id="0196e69a35ffc71ef5b9738fc38bb6be")],
    invalid_tool_calls=[],
    usage_metadata={
              "input_tokens": 47838,
              "output_tokens": 20099,
              "total_tokens": 67937,
              "input_token_details": {},
              "output_token_details": {"reasoning": 18722}
              }
)

FINAL_MESSAGE = AIMessage(
    content="\n\n法国的首都是**巴黎（Paris）**。巴黎是法国最大的城市，也是欧洲第二大城市，位于法国北部的巴黎盆地中央，横跨塞纳河两岸。作为法国的政治、经济、文化中心，巴黎不仅是世界著名的旅游目的地，还以悠久的历史、艺术遗产和浪漫氛围闻名。\n\n如果您还有其他问题，或者需要更详细的信息，请随时告诉我！",
    tool_calls=[],
    invalid_tool_calls=[],
    usage_metadata={
              "input_tokens": 344040,
              "output_tokens": 16652,
              "total_tokens": 360692,
              "input_token_details": {},
              "output_token_details": {"reasoning": 14375}
              }
)

PREDEFINED_REPLIES_MESSAGES = [TOOL_CALL_MESSAGE, FINAL_MESSAGE]