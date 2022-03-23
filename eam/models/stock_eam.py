import time
import json
import requests
import pandas as pd
import collections


class InsertEam:

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8"}
        self.data_list = []

    def login(self, username, password):
        logurl = "https://eam.cti-cert.com/common/login.do"
        logdata = {
            "account": username,
            "password": password,
            'isFirst': 'true'
        }
        S = self.session.post(logurl, data=logdata)


    def findDepartTable(self):
        cccc = self.session.post(
            'https://eam.cti-cert.com/sysOrg/search.do?txnCode=PURCHASE_APPLYMATERIAL&columnTxnCode=SYS_ORG&isDataAllot=true&_dc=1632880613505').json()
        df = pd.DataFrame(cccc["results"])
        df = pd.DataFrame(df, columns=['name', 'id'])
        df_dict = dict(collections.OrderedDict(
            zip(df.iloc[:, 0], df.iloc[:, 1])))
        del df_dict['苏州华测生物技术有限公司']
        return df_dict

    def findDepartId(self, department):
        df_dict = self.findDepartTable()
        dept_id = [x[1] for x in df_dict.items() if department in x[0]]
        dept_name = [x[0] for x in df_dict.items() if department in x[0]]
        dept_list = dept_name + dept_id
        return dept_list

    def findProjectInf(self, code):
        url_search = 'https://eam.cti-cert.com/baseMaterialXZ/search.do?txnCode=PURCHASEXZ_APPLYMATERIAL&columnTxnCode=BASE_MATERIALXZ'
        search_date = {"column": "matCode",
                       "type": "string",
                       "condition": "like",
                       "value": code
                       }
        data = {'searchJson': json.dumps([search_date]),
                'page': 1,
                'start': 0,
                'limit': 50
                }

        find_inf_result = self.session.post(
            url_search, data=data).json()['results'][0]
        return find_inf_result

    def findOrderInf(self):
        ccc = self.session.post(
            'https://eam.cti-cert.com/formPageForward.do?txnCode=PURCHASEXZ_APPLYMATERIAL&action=save&selectedId=&panelName=PurchaseXZApplyMaterialPanel&dynamicFormListenersPath=/pages/purchaseXZ/purchaseXZApplyMaterial/dynamicForm_listeners.js&tabId=purchaseXZApplyMaterialsave&rawTxnCode=&printTxnCode=&TABID=purchaseXZApplyMaterialsave').text
        c1 = ccc.find('applyNo:')
        c2 = ccc.find('jbpmProcessId:')
        applyid = ccc[c1:c2 - 1][ccc[c1:c2 -
                                     1].find("'") + 1:ccc[c1:c2 - 1].rfind("'", 1)]
        applydate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        return [applyid, applydate]

    def del_data(self, df1):

        func = {'name': 'count'}
        df2 = df1.groupby('name').agg(func)
        data = {
            'department': '信息',
            'code': list(df2.index),
            'number': list(df2['name']),
        }
        return data

    def compute(self, df, start, number):
        sum_1 = 0
        for i in range(start, number):
            sum_1 += float(df['price'][i])
            if sum_1 >= 300:
                df1 = df.iloc[start:i+1, :]
                data = self.del_data(df1)
                self.data_list.append(data)
                start = i+1
                return self.compute(df, i+1, number)
            elif i+1 == number and sum_1 < 300:
                df1 = df.iloc[start:, :]
                data = self.del_data(df1)
                self.data_list.append(data)
                return self.data_list
            else:
                pass

        data_list = self.compute_child(start, number)
        return data_list

    def AssembleData(self, code_list, num_list, department, user):
        apply_goods = []
        for i, j in enumerate(code_list):
            find_inf_result = self.findProjectInf(j)
            total = str(num_list[i]*float(find_inf_result['newPrice']))
            apply_good = {"id": "new_232e84fb86ef4784b7cb0c5eb4cce732235",
                          "supplierspriceId": "",
                          "materialId": find_inf_result['id'],
                          "name": find_inf_result['name'],
                          "type": find_inf_result['matType'],
                          "factoryName": find_inf_result['factoryName'],
                          "cas": "",
                          "partNo": find_inf_result['partNo'],
                          "unit": find_inf_result['unit'],
                          "num": num_list[i],
                          "use": "",
                          "price": find_inf_result['newPrice'],
                          "bidPrice": "",
                          "total": total,
                          "remark": "",
                          "applyStatus": 1,
                          "orderStatus": 1,
                          "claimStatus": 1,
                          "applyId": "",
                          "budgeId": "",
                          "claimUserName": "",
                          "claimUser": "",
                          "arrivalDate": "",
                          "arrivalNum": 0,
                          "orderNum": 0,
                          "claimingTime": "",
                          "claimTime": "",
                          "claimRemark": "",
                          "status": 0,
                          "createTime": "",
                          "createUser": "",
                          "modUser": "",
                          "modTime": "",
                          "deptId": "",
                          "deptName": "",
                          "applyNo": "",
                          "orderNo": ""}
            apply_goods.append(apply_good)
            find_order_inf = self.findOrderInf()
            department_and_id = self.findDepartId(department)
            print(department_and_id)
            data = {
                'jbpmProcessId': '40284d815a8e8eaa015a8e98bad40001',
                'deptName': department_and_id[0],
                'applyNo': find_order_inf[0],
                'applyUser': user,
                'applyDate': find_order_inf[1],
                'total': 0,
                'status': 1,
                'DevUtil-DynamicForm-ext-28_purchaseXZApplyMaterialDetSubGrid_filter-inputEl': '物品名称',
                'deptId': department_and_id[1],
                'purchaseXZApplyMaterialDetJsonData': json.dumps(apply_goods)
            }
            return data

    def AddOrder(self, code_list, num_list, department, user):
        url = 'https://eam.cti-cert.com/purchaseXZApplyMaterial/sp/submit.do?txnCode=PURCHASEXZ_APPLYMATERIAL_SAVE'
        if department != '公共':
            data = self.AssembleData(code_list, num_list, department, user)
            response = self.session.post(
                url, headers=self.headers, data=data).text
            print(response)

        else:
            price_list = [self.findProjectInf(
                i)['newPrice'] for i in code_list]
            if len(price_list) == len(code_list) and len(code_list) == len(num_list):
                list1 = [[code_list[i]]*num_list[i]
                         for i in range(len(code_list))]
                code_list_list = sum([[code_list[i]]*num_list[i]
                                     for i in range(len(code_list))], [])
                price_list_list = sum([[price_list[i]]*num_list[i]
                                      for i in range(len(code_list))], [])
                data1 = {'name': code_list_list, 'price': price_list_list,
                         'number': range(1, sum(num_list)+1)}
                df = pd.DataFrame(data1)
                data_list = self.compute(df, 0, sum(num_list))
                print(data_list)

                for i in data_list:
                    child_department = i['department']
                    child_code = i['code']
                    child_number = i['number']
                    data = self.AssembleData(
                        child_code, child_number, child_department, user)
                    response = self.session.post(
                        url, headers=self.headers, data=data).text
                    print(response)


if __name__ == '__main__':
    username = '48502'
    password = '123'
    order = InsertEam()
    order.login(username, password)
    code_list = ['WA01001.100924.306']
    department = '信息'
    user = '张铭'
    order.AddOrder(code_list, [10], department, user)
