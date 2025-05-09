
from datetime import datetime
import json
from flask import Flask, jsonify, request
from sqlalchemy import func

from data.dataset import PreferenceConfig, PreferenceConfigDetail, User, WeeklyReport, WeeklyReportTemplate, get_db
# from wrapper.openai import get_agent_executor
from model.result import Result

from flask_cors import CORS, cross_origin

from wrapper.openai import get_agent_executor
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
@app.route('/api/weekly_report/hello', methods=['POST'])
@cross_origin()
def hello_world():
   return {
      "result": 'Hello World'
   }
from datetime import datetime

def get_time():
        # 获取当前系统时间
    now = datetime.now()

    # 获取年和月
    year = now.year
    month = now.month
    # 计算当月的第几个周五
    first_day_of_month = datetime(year, month, 1)
    first_friday = first_day_of_month
    while first_friday.weekday() != 4:  # 4 corresponds to Friday
        first_friday = first_friday.replace(day=first_friday.day + 1)
    # Calculate the week number of the first Friday
    week_number = (first_friday.day - 1) // 7 + 1
    term = week_number
    return year,month,term


from flask import Flask, jsonify, request, g
import requests

@app.before_request
def check_fusion_auth_header():
    if( request.headers.get('isMock') or True):
        g.user_info = {
                "id": "2",
                "userFullname": "2025000559",
        }
        return

    fusion_auth_header = request.headers.get('fusion-auth')

    dev_url = 'http://106.63.7.106:10001/api/user/info'
    # url = 'https://c4ai.ccccltd.cn/api/user/info'
    def fetch_user_info():
        headers = {
            'fusion-auth': fusion_auth_header
        }
        try:
            response = requests.get(dev_url, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses
            return response.json()
        except requests.RequestException:
            return None
    response = fetch_user_info()
    if response['code'] == 8000000:
        g.user_info = response['data']
    # Fetch user info and store it in the global object
    # g.user_info = fetch_user_info()
    if not g.user_info:
         return jsonify({"status": "400", "msg": "Valid 'fusion-auth' header is required"}), 400
    



@app.route("/api/weekly_report/message", methods=['POST'])
def message():
   if request.method == 'POST':
      data = request.get_json()
      session_id = str(data.get('sessionId'))
      message_info = str(data.get('messageInfo'))
      executor = get_agent_executor(session_id)
      result = executor.invoke(
          {"input": message_info},
          config={"configurable": {"session_id": session_id}},
      )
      return Result(200,result['output']).to_json()
   else:
      return Result(400,'This route only handles POST requests.').to_json()


@app.route('/api/weekly_report/initialize-users', methods=['POST'])
def initialize_users():
    data = request.get_json()
    usernames = data.get('usernames', [])

    if not usernames:
        return jsonify({"status": "400", "msg": "Usernames list is required"})

    db = get_db()
    try:
        for username in usernames:
            user = User(
                username=username,
                department_id=1,  # 默认部门ID
                password='0',     # 默认密码
                is_deleted=0
            )
            db.add(user)
        db.commit()
        return jsonify({"status": "200", "msg": "Users initialized successfully"})
    except Exception as e:
        db.rollback()
        return jsonify({"status": "500", "msg": str(e)})
    finally:
        db.close()


@app.route('/api/weekly_report/user-config-details', methods=['GET'])
def get_user_config_details():
    # user_id = request.args.get('user_id', type=int)
    userInfo = g.get('user_info', None)
    user_id = userInfo['id']
    db = get_db()
    try:
        # 查询用户的配置明细
        config_details = db.query(PreferenceConfigDetail).filter_by(user_id=user_id).all()
        
        # 构建返回数据
        data = [
            {
                "id": detail.id,
                # "config_id": detail.config_id,
                "content": detail.content,
                "created_at": detail.created_at,
                "updated_at": detail.updated_at,
                "extra": detail.extra
            } for detail in config_details
        ]

        return jsonify({"status": "200", "data": data})
    except Exception as e:
        return jsonify({"status": "500", "msg": str(e)})
    finally:
        db.close()

@app.route('/api/weekly_report/config-detail', methods=['POST'])
def add_config_detail():
    data = request.get_json()
    # user_id = data.get('user_id')
    config_id = data.get('config_id') if 'config_id' in data else 1
    content = data.get('content')
    extra = data.get('extra', None)
    userInfo = g.get('user_info', None)
    user_id = userInfo['id']
    if not user_id or not config_id or not content:
        return jsonify({"status": "400", "msg": "user_id, config_id, and content are required"})

    db = get_db()
    try:
        # 添加新的配置明细
        detail = PreferenceConfigDetail(
            user_id=user_id,
            config_id=config_id,
            content=content,
            extra=extra
        )
        db.add(detail)
        db.commit()
        return jsonify({"status": "200", "msg": "Config detail added successfully", "data": {
            "id": detail.id,
            "user_id": detail.user_id,
            # "config_id": detail.config_id,
            "content": detail.content,
            "created_at": detail.created_at,
            "updated_at": detail.updated_at,
            "extra": detail.extra
        }})
    except Exception as e:
        db.rollback()
        return jsonify({"status": "500", "msg": str(e)})
    finally:
        db.close()

@app.route('/api/weekly_report/config-detail/<int:detail_id>', methods=['PUT'])
def update_config_detail(detail_id):
    data = request.get_json()
    userInfo = g.get('user_info', None)
    user_id = userInfo['id']
    config_id = data.get('config_id') if 'config_id' in data else 1

    content = data.get('content')
    extra = data.get('extra', None)

    if not user_id or not config_id or not content:
        return jsonify({"status": "400", "msg": "user_id, config_id, and content are required"})

    db = get_db()
    try:
        # 更新配置明细
        detail = db.query(PreferenceConfigDetail).filter_by(id=detail_id, user_id=user_id).first()
        if not detail:
            return jsonify({"status": "404", "msg": "Config detail not found"})
        detail.config_id = config_id
        detail.content = content
        detail.extra = extra
        db.commit()
        return jsonify({"status": "200", "msg": "Config detail updated successfully", "data": {
            "id": detail.id,
            "user_id": detail.user_id,
            # "config_id": detail.config_id,
            "content": detail.content,
            "created_at": detail.created_at,
            "updated_at": detail.updated_at,
            "extra": detail.extra
        }})
    except Exception as e:
        db.rollback()
        return jsonify({"status": "500", "msg": str(e)})
    finally:
        db.close()


@app.route('/api/weekly_report/config-detail/<int:detail_id>', methods=['DELETE'])
def delete_config_detail(detail_id):
    db = get_db()
    try:
        # 查找要删除的配置明细
        detail = db.query(PreferenceConfigDetail).filter_by(id=detail_id).first()
        if not detail:
            return jsonify({"status": "404", "msg": "Config detail not found"})

        # 删除配置明细
        db.delete(detail)
        db.commit()
        return jsonify({"status": "200", "msg": "Config detail deleted successfully"})
    except Exception as e:
        db.rollback()
        return jsonify({"status": "500", "msg": str(e)})
    finally:
        db.close()

@app.route('/api/weekly_report/weekly-reports', methods=['GET'])
def get_weekly_reports():
   #  user_id = request.args.get('user_id', type=int)
    type = request.args.get('type', type=int)

    db = get_db()

    try:
        # 获取status=1的周报，根据年月日进行排序，距离现在最近的越靠前
        reports = db.query(WeeklyReport).filter(
            WeeklyReport.type == type,
            WeeklyReport.status == 1,
            WeeklyReport.is_deleted == 0
        ).order_by(
            WeeklyReport.year.desc(),
            WeeklyReport.month.desc(),
            WeeklyReport.term.desc()
        ).all()
        aggregated_reports = []
        current_group = None
        for report in reports:
            if (current_group is None or 
                current_group['year'] != report.year or 
                current_group['month'] != report.month or 
                current_group['term'] != report.term):
                
                if current_group is not None:
                    aggregated_reports.append(current_group)
                
                current_group = {
                    'year': report.year,
                    'month': report.month,
                    'term': report.term,
                    'data': []
                }
            
            current_group['data'].append({
                "id": report.id,
                "user_id": report.user_id,
                "username": report.user_name,
                # "department": report.department,
                "item": report.item,
                "year": report.year,
                "month": report.month,
                "term": report.term,
                "work_this_week": report.work_this_week,
                "plan_next_week": report.plan_next_week,
                "version": report.version,
                "raw_content": report.raw_content,
                "created_at": report.created_at,
                "updated_at": report.updated_at,
                "extra": report.extra
            })
        
        if current_group is not None:
            aggregated_reports.append(current_group)

        # data = aggregated_reports
        userInfo = g.get('user_info', None)
        user_id = userInfo['id']
        year,month,term =get_time()
        # INSERT_YOUR_CODE
        # Filter aggregated_reports to only include reports for the current user
        filtered_reports = []
        for group in aggregated_reports:
            if group['year'] == year and group['month'] == month and group['term'] == term:
                filtered_group = {
                    'year': group['year'],
                    'month': group['month'],
                    'term': group['term'],
                    'data': [report for report in group['data'] if report['user_id'] == user_id]
                }
                if filtered_group['data']:
                    filtered_reports.append(filtered_group)
            else:
                filtered_reports.append(group)
        
        data = filtered_reports

        return jsonify({"status": "200", "data": data})
    except Exception as e:
        return jsonify({"status": "500", "msg": str(e)})
    finally:
        db.close()


@app.route('/api/weekly_report/weekly-report-history', methods=['GET'])
def get_weekly_report_history():
    year,month,term = get_time()
    type = request.args.get('type', type=int)
    userInfo = g.get('user_info', None)
    user_id = userInfo['id']

    if not all([year, month, term]):
        return jsonify({"status": "400", "msg": "year, month, and term are required"})
    db = get_db()
    try:
        # 查询指定某人的年、月、期数的所有周报版本
        reports = db.query(WeeklyReport).filter_by(
            year=year,
            month=month,
            term=term,
            user_id=user_id,
            type=type,
            is_deleted=0,
            status =0
        ).order_by(WeeklyReport.version.desc()).limit(10).all()
        # INSERT_YOUR_CODE
        # 按照版本数进行聚合
        version_groups = {}
        for report in reports:
            version = report.version
            if version not in version_groups:
                version_groups[version] = {
                    "version": version,
                    "reports": []
                }
            version_groups[version]["reports"].append({
                "id": report.id,
                "user_id": report.user_id,
                "department": report.department,
                "item": report.item,
                "year": report.year,
                "month": report.month,
                "term": report.term,
                "work_this_week": report.work_this_week,
                "plan_next_week": report.plan_next_week,
                "raw_content": report.raw_content,
                "created_at": report.created_at,
                "updated_at": report.updated_at,
                "extra": report.extra
            })

        # 将版本组转换为列表并按版本号降序排序
        aggregated_data = sorted(version_groups.values(), key=lambda x: x["version"], reverse=True)
        # # 构建返回数据
        # data = [
        #     {
        #         "id": report.id,
        #         "user_id": report.user_id,
        #         "department": report.department,
        #         "item": report.item,
        #         "year": report.year,
        #         "month": report.month,
        #         "term": report.term,
        #         "work_this_week": report.work_this_week,
        #         "plan_next_week": report.plan_next_week,
        #         "version": report.version,
        #         "raw_content": report.raw_content,
        #         "created_at": report.created_at,
        #         "updated_at": report.updated_at,
        #         "extra": report.extra
        #     } for report in reports
        # ]

        return jsonify({"status": "200", "data": aggregated_data})
    except Exception as e:
        return jsonify({"status": "500", "msg": str(e)})
    finally:
        db.close()

@app.route('/api/weekly_report/weekly-report/<int:report_id>', methods=['PUT'])
def update_weekly_report(report_id):
    data = request.get_json()

    # 检查请求体中是否包含需要更新的字段
    if not data:
        return jsonify({"status": "400", "msg": "No data provided for update"})

    db = get_db()
    try:
        # 查找要更新的周报
        report = db.query(WeeklyReport).filter_by(id=report_id, is_deleted=0).first()
        if not report:
            return jsonify({"status": "404", "msg": "Weekly report not found"})

        # 更新周报字段
        for key, value in data.items():
            if hasattr(report, key):
                setattr(report, key, value)

        db.commit()
        return jsonify({"status": "200", "msg": "Weekly report updated successfully", "data": {
            "id": report.id,
            "user_id": report.user_id,
            "department": report.department,
            "item": report.item,
            "year": report.year,
            "month": report.month,
            "term": report.term,
            "work_this_week": report.work_this_week,
            "plan_next_week": report.plan_next_week,
            "version": report.version,
            "raw_content": report.raw_content,
            "created_at": report.created_at,
            "updated_at": datetime.now(),
            "extra": report.extra
        }})
    except Exception as e:
        db.rollback()
        return jsonify({"status": "500", "msg": str(e)})
    finally:
        db.close()


@app.route('/api/weekly_report/weekly-report', methods=['POST'])
def add_weekly_report():
    data = request.get_json()
    # 检查请求体中是否包含所有必要字段
    required_fields = [ 'type', 'work_this_week', 'plan_next_week', 'raw_content','status']
    if not all(field in data for field in required_fields):
        return jsonify({"status": "400", "msg": "Missing required fields"})
    db = get_db()
    year,month,term = get_time()

    try:
        userInfo = g.get('user_info', None)
        user_id = userInfo['id']
        username = userInfo['userFullname']
        if data['status'] == 1:
            # 查询是否存在相同用户id、年、月、期数的记录
            existing_reports = db.query(WeeklyReport).filter_by(
                user_id=user_id,
                year=year,
                month=month,
                term=term,
                type = data['type'],
                is_deleted=0,
                status=1
            ).all()

            # 如果存在，将is_deleted标记为1
            for report in existing_reports:
                report.is_deleted = 1
            db.commit()

        # 查询当前年、月、期数的最大版本号
        max_version = db.query(func.max(WeeklyReport.version)).filter_by(
            year=year,
            month=month,
            term=term,
            user_id=user_id,
            is_deleted=0
        ).scalar() or 0

        # 新版本号为最大版本号加 1
        new_version = max_version + 1

        # 创建新的周报对象
        report = WeeklyReport(
            user_id=user_id,
            user_name= username, 
            # department=data['department'],
            item=data.get('item', None),  # Use .get() to handle missing 'item' field
            year=year,
            month=month,
            term=term,
            type=data['type'],
            work_this_week=data['work_this_week'],
            plan_next_week=data['plan_next_week'],
            version=new_version,
            raw_content=data.get('raw_content',None),
            extra=data.get('extra', None),
            is_deleted=0,
            status = 0
        )
        db.add(report)
        db.commit()

        if data['status']==1:
            report = WeeklyReport(
                user_id=user_id,
                user_name= username, 
                # department=data['department'],
                item=data.get('item', None),
                year=year,
                month=month,
                term=term,
                type=data['type'],
                work_this_week=data['work_this_week'],
                plan_next_week=data['plan_next_week'],
                version=new_version,
                raw_content=data.get('raw_content',None),
                extra=data.get('extra', None),
                is_deleted=0,
                status = 1
            )
            db.add(report)
            db.commit()

        return jsonify({"status": "200", "msg": "Weekly report added successfully"})
    except Exception as e:
        db.rollback()
        return jsonify({"status": "500", "msg": str(e)})
    finally:
        db.close()


@app.route('/api/weekly_report/weekly-reports', methods=['POST'])
def add_weekly_reports():
    data = request.get_json()
    # 检查请求体中是否包含所有必要字段
    required_fields = ['type', 'records','status']
    if not all(field in data for field in required_fields):
        return jsonify({"status": "400", "msg": "Missing required fields"})
    userInfo = g.get('user_info', None)
    user_id = userInfo['id']
    username = userInfo['userFullname']
    db = get_db()
    year,month,term = get_time()
    # 'item', 'work_this_week', 'plan_next_week', 'raw_content','status'
    records = data.get('records', [])
    if not records:
        return jsonify({"status": "400", "msg": "Records list is required"})  
    # Get the status from the first record
 

    try:

        if data['status'] == 1:
            # 查询是否存在相同用户id、年、月、期数的记录
            existing_reports = db.query(WeeklyReport).filter_by(
                user_id=user_id,
                year=year,
                month=month,
                term=term,
                is_deleted=0,
                status=1
            ).all()

            # 如果存在，将is_deleted标记为1
            for report in existing_reports:
                report.is_deleted = 1
            db.commit()

        # 查询当前年、月、期数的最大版本号
        max_version = db.query(func.max(WeeklyReport.version)).filter_by(
            year=year,
            month=month,
            term=term,
            user_id=user_id,
            is_deleted=0
        ).scalar() or 0

        # 新版本号为最大版本号加 1
        new_version = max_version + 1


        for record in records:
            report = WeeklyReport(
                user_id=user_id,
                user_name=username,
                # department=data['department'],
                year=year,
                month=month,
                term=term,
                type=data['type'],
                item=record.get('item'),
                work_this_week=record.get('work_this_week'),
                plan_next_week=record.get('plan_next_week'),
                raw_content=record.get('raw_content'),
                extra=record.get('extra', None),
                version=new_version,
                is_deleted=0,
                status=0
            )
            db.add(report)
        db.commit()

        if data['status']==1:
            for record in records:
                report = WeeklyReport(
                    user_id=user_id,
                    user_name=username,
                    # department=data['department'],
                    item=record.get('item'),
                    year=year,
                    month=month,
                    term=term,
                    type=data['type'],
                    work_this_week=record.get('work_this_week'),
                    plan_next_week=record.get('plan_next_week'),
                    version=new_version,
                    raw_content=record.get('raw_content'),
                    extra=record.get('extra', None),
                    is_deleted=0,
                    status=1
                )
                db.add(report)
            db.commit()
        return jsonify({"status": "200", "msg": "Weekly report added successfully"})
    except Exception as e:
        db.rollback()
        return jsonify({"status": "500", "msg": str(e)})
    finally:
        db.close()





@app.route('/api/weekly_report/weekly-report-template', methods=['POST'])
def add_weekly_report_template():
    data = request.get_json()

    # Check if all required fields are present
    required_fields = ['username', 'department_id', 'content']
    if not all(field in data for field in required_fields):
        return jsonify({"status": "400", "msg": "Missing required fields"})

    db = get_db()
    try:
        # Create a new WeeklyReportTemplate object
        template = WeeklyReportTemplate(
            username=data['username'],
            department_id=data['department_id'],
            content=data['content'],
            extra=data.get('extra', None),
            is_deleted=0
        )
        db.add(template)
        db.commit()
        return jsonify({"status": "200", "msg": "Weekly report template added successfully", "data": {
            "id": template.id,
            "username": template.username,
            "department_id": template.department_id,
            "content": template.content,
            "created_at": template.created_at,
            "updated_at": template.updated_at,
            "extra": template.extra
        }})
    except Exception as e:
        db.rollback()
        return jsonify({"status": "500", "msg": str(e)})
    finally:
        db.close()

from langgraph_sdk import get_sync_client
from flask import Flask, Response
@app.route("/api/weekly_report/sse-message", methods=['POST'])
def sse_message():
    # Capture request arguments within the request context
    data = request.get_json()
    session_id = str(data.get('sessionId'))
    message_info = str(data.get('messageInfo'))
    client = get_sync_client(url="http://localhost:2024")

    def generate():
        for chunk in client.runs.stream(
            None,  # Threadless run
            "agent", # Name of assistant. Defined in langgraph.json.
            input={
                "messages": [{
                    "role": "user",
                    "content": message_info,
                }],
            },
            stream_mode=["updates","custom"],
        ):
            print(f"Receiving new event of type: {chunk.event}...")
            print(chunk.data)
            print("\n\n")
            combined_data = {
                "event": chunk.event,
                "data": chunk.data
            }
            yield json.dumps(combined_data, ensure_ascii=False)
            # yield json.dumps({"event_type": f'{chunk.event}', "data": f'{chunk.data}'})

    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=5000)