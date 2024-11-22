from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 数据文件路径
DATA_FILE_PATH = 'services/backend/src/sankey_data.csv'

@app.route('/api/filter-options', methods=['GET'])
def get_filter_options():
    """
    返回每个节点对应的可选值，用于前端过滤器的下拉框
    """
    try:
        df = pd.read_csv(DATA_FILE_PATH)

        # 获取每列的唯一值
        filter_options = {col: sorted(df[col].unique().tolist()) for col in df.columns}

        return jsonify(filter_options)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sankey-data', methods=['POST'])
def get_sankey_data():
    """
    根据前端传递的节点选择和过滤条件动态生成 Sankey 数据
    """
    try:
        # 获取前端传递的数据
        request_data = request.get_json()
        nodes = request_data.get("nodes", [])
        filters = request_data.get("filters", {})

        # 读取数据
        df = pd.read_csv(DATA_FILE_PATH)

        # 根据 filters 过滤数据
        for column, values in filters.items():
            if values:  # 如果有选中的过滤条件
                df = df[df[column].isin(values)]

        # 构建 Sankey 图所需的节点和链接数据
        labels = []
        for node in nodes:
            labels.extend(df[node].unique().tolist())
        labels = sorted(set(labels))  # 去重排序

        # 动态为每个标签分配颜色
        color_map = {}
        colors = [
            "gray", "purple", "blue", "orange", "green", "red",
            "lightblue", "pink", "yellow", "brown", "cyan"
        ]
        for i, label in enumerate(labels):
            color_map[label] = colors[i % len(colors)]  # 循环分配颜色

        # 构建 source, target, value
        source = []
        target = []
        value = []

        for _, row in df.iterrows():
            for i in range(len(nodes) - 1):
                source_label = row[nodes[i]]
                target_label = row[nodes[i + 1]]
                source_idx = labels.index(source_label)
                target_idx = labels.index(target_label)

                # 检查 source 和 target 是否已经存在，避免重复
                if (source_idx, target_idx) not in zip(source, target):
                    source.append(source_idx)
                    target.append(target_idx)
                    value.append(1)
                else:
                    idx = list(zip(source, target)).index((source_idx, target_idx))
                    value[idx] += 1

        # 构建 JSON 格式
        sankey_data = {
            "nodes": {
                "label": labels,
                "color": [color_map[label] for label in labels],
            },
            "links": {
                "source": source,
                "target": target,
                "value": value,
            },
        }

        return jsonify(sankey_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
