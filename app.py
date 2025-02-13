from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# 加载 JSON 数据
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# 加载所有 JSON 文件
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'relic')

relics_data = load_json(os.path.join(DATA_DIR, 'relics.json'))
ornaments_data = load_json(os.path.join(DATA_DIR, 'ornaments.json'))
relics_entry_host_data = load_json(os.path.join(DATA_DIR, 'entry', 'host', 'relics.json'))
ornaments_entry_host_data = load_json(os.path.join(DATA_DIR, 'entry', 'host', 'ornaments.json'))
entry_deputy_data = load_json(os.path.join(DATA_DIR, 'entry', 'deputy.json'))

def get_entry_host_id(selected_part, relic_entry_data, main_attributes):
        for entry in relic_entry_data:
            if entry['part'] == selected_part and entry['attribute'] in main_attributes:
                entry_id = entry['id']
                return entry_id

def get_entry_deputy_id(attr, entry_data, main_attributes):
    for entry in entry_data:
        if entry['attribute'] == attr and entry['attribute'] in main_attributes:
            entry_id = entry['id']
            return entry_id

@app.route('/')
def index():
    return render_template('index.html')

# 提供 JSON 数据的 API 接口
@app.route('/api/data', methods=['GET'])
def get_data():
    category = request.args.get('category')
    if category == "隧洞遗器":
        response = jsonify(relics_data)
    elif category == "位面饰品":
        response = jsonify(ornaments_data)
    else:
        response = jsonify({"error": "Invalid category"}), 400

    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/api/data/entry/host', methods=['GET'])
def get_data_entry_host():
    category = request.args.get('category')
    if category == "隧洞遗器":
        response = jsonify(relics_entry_host_data)
    elif category == "位面饰品":
        response = jsonify(ornaments_entry_host_data)
    else:
        response = jsonify({"error": "Invalid category"}), 400

    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/api/data/entry/deputy', methods=['GET'])
def get_data_entry_deputy():
    category = request.args.get('category')
    if category == "隧洞遗器":
        response = jsonify(entry_deputy_data)
    elif category == "位面饰品":
        response = jsonify(entry_deputy_data)
    else:
        response = jsonify({"error": "Invalid category"}), 400

    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/get_command', methods=['POST'])
def get_command():
    data = request.json
    category = data.get('category')
    selected_set = data.get('set')
    selected_part = data.get('part')
    selected_level = data.get('level')
    print(data)

    # 处理复选框状态
    main_attributes = [key[5:] for key in request.json if key.startswith('main_') and request.json[key]]
    deputy_attributes = [key[7:] for key in request.json if key.startswith('deputy_') and request.json[key] and not key.endswith('_value')]

    print("main_attributes", main_attributes)
    print("deputy_attributes", deputy_attributes)

    if category == "隧洞遗器":
        relic_data = relics_data
        relic_entry_data = relics_entry_host_data
    elif category == "位面饰品":
        relic_data = ornaments_data
        relic_entry_data = ornaments_entry_host_data
    else:
        return jsonify({"error": "Invalid category"}), 400

    try:
        if selected_set in relic_data and selected_part in relic_data[selected_set]:
            item_id = relic_data[selected_set][selected_part]
            print("main_attributes", main_attributes)
            if len(main_attributes) == 0:
                command = f"/give {item_id}"
                response = jsonify({'command': command})  # 返回 JSON 响应
                response.headers['Content-Type'] = 'application/json; charset=utf-8'  # 设置 Content-Type
                return response
            else:
                entry_id = get_entry_host_id(selected_part, relic_entry_data, main_attributes)
                print("deputy_attributes", deputy_attributes)
                if len(deputy_attributes) == 0:
                    command = f"/relic {item_id} l{selected_level} {entry_id}"
                    response = jsonify({'command': command})  # 返回 JSON 响应
                    response.headers['Content-Type'] = 'application/json; charset=utf-8'  # 设置 Content-Type
                    return response
                elif 0 < len(deputy_attributes) <= 4:
                    command = f"/relic {item_id} l{selected_level} {entry_id}"
                    for attr in deputy_attributes:
                        command += f" {get_entry_deputy_id(attr, entry_deputy_data, deputy_attributes)}:{data.get(f'deputy_{attr}_value', 0)}"
                    response = jsonify({'command': command})  # 返回 JSON 响应
                    response.headers['Content-Type'] = 'application/json; charset=utf-8'  # 设置 Content-Type
                    return response
                else:
                    return jsonify({"error": "非正确的副属性内容"}), 400
        else:
            return jsonify({"error": "Invalid selection"}), 400
    except Exception as e:
        print({"error": str(e)})
        return jsonify({"error": str(e)}), 500  # 返回 500 错误


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)