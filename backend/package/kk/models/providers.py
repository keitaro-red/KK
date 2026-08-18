"""内置模型供应商定义"""
BUILTIN_PROVIDERS = [
    {
        "provider_id":"siliconflow-cn",     # 供应商标识
        "displayname":"SiliconFlow",        # 显示名
        "base_url":"https://api.siliconflow.cn/v1",     
        "api_key_env":"SILICONFLOW_API_KEY",        
        "enable_models":[
            {
                "id":"deepseek-ai/DeepSeek-V4-Flash",
                "type":"chat",
                "display_name":"DeepSeek-V4-Flash",
            },
        ],
    },
]