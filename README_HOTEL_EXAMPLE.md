# 酒店查询示例使用说明

## 简介

`run_hotel_example.py` 是一个演示脚本，用于展示如何使用 Owl 框架中的 `HotelToolkit` 进行酒店查询和推荐。该脚本使用 Azure OpenAI 服务来处理自然语言查询，并通过 `HotelToolkit` 提供的工具函数来获取酒店信息和推荐。

## 前提条件

在运行此脚本之前，您需要满足以下条件：

1. 安装所有必要的依赖项（可在项目根目录运行 `pip install -r requirements.txt`, 具体可参考README.md/README_zh.md）
2. 配置 Azure OpenAI API 凭据（在 `.env` 文件中设置）

## 环境变量配置

在项目根目录创建一个 `.env` （可参考 `.env_template`）文件，并设置以下环境变量：

```
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_API_VERSION=your_api_version
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT=your_deployment
AZURE_OPENAI_MODEL=your_model_name
```

## 使用方法

### 基本用法

直接运行脚本即可启动酒店查询示例：

```bash
python run_hotel_example.py
```

默认情况下，脚本会使用预设的查询："我需要预订杭州的一个酒店：2025年3月9日，1天的酒店，经纬度（120.026208, 30.279212）。请一步步处理：第一步，你自己选择一个不错的酒店，第二步，帮我选择一个房间。最后告诉我你选择的详细信息"

### 自定义查询

如果您想使用自定义查询，可以修改脚本中的 `question` 变量：

```python
# 示例问题
question = "我需要预订上海的一个酒店：2025年4月15日，2天的酒店，靠近外滩。我需要有免费早餐的房间。"

society = construct_society(question)
answer, chat_history, token_count = run_society(society)
```

## 工作原理

1. 脚本首先加载环境变量和必要的依赖项
2. 创建用户和助手模型实例（使用 Azure OpenAI）
3. 初始化 `HotelToolkit` 并获取其工具函数
4. 构建一个 `OwlRolePlaying` 社会，包含用户和助手角色
5. 运行社会模拟，处理酒店查询请求
6. 输出查询结果

## 核心组件

- **HotelToolkit**: 提供酒店查询和推荐功能的工具包
- **OwlRolePlaying**: 模拟用户和助手之间的对话
- **ModelFactory**: 创建和配置 AI 模型实例

## 示例输出

成功运行后，脚本将输出类似以下内容的酒店推荐：

```
Answer: 我已经为您选择了一家位于杭州的酒店，详情如下：

选择的酒店：杭州菲住布渴酒店
- 地址：文一西路969号乐淘城8号楼
- 星级：4星（高档型）
- 评分：4.7/5
- 距离您指定位置：440米
- 价格：起价¥599/晚

推荐房间：豪华大床房
- 床型：1张2米大床
- 面积：28平方米
- 含早餐
- 免费WiFi
- 空调、电视、独立卫浴等标准设施

这家酒店位于杭州未来科技城区域，靠近您提供的经纬度位置，步行仅需5分钟。酒店环境优雅，服务设施完善，包括共享办公空间、叫醒服务和洗衣服务等。房间宽敞舒适，非常适合商务或休闲旅行。

您可以通过酒店官网或主流订房平台预订这家酒店。如需更多信息或其他选择，请告知我。
```

## 故障排除

如果遇到问题，请检查：

1. 环境变量是否正确设置
2. 网络连接是否正常
3. Azure OpenAI 服务是否可用
4. 日志输出中是否有错误信息

## 贡献

如果您想为这个项目做出贡献，请随时提交 Pull Request 或创建 Issue。
