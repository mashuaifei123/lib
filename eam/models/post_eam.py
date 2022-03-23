import time
import json
import requests
import pandas as pd
import collections


class PostDepartmentEam:

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
    

    def getPassTime(self, applyid_list):

        """通过申请单号获得是否审批信息"""
        url = 'https://eam.cti-cert.com/purchaseApplyMaterialAgreed/searchLocalhost.do?txnCode=PURCHASE_APPLYMATERIALAGREED_SEARCH&_dc=1637118990742'
        orderpass_list=[]
        for i in applyid_list:
            try:
                data = {'searchJson': json.dumps([{"column": "applyNo", "type": "string", "condition": "like", "value": i}]),
                        'page': 1,
                        'start': 0,
                        'limit': 50}
                order_pass_url = self.session.post(url=url, headers=self.headers, data=data).json()

                info={'apply_id' : i, 'modtime':order_pass_url["results"][0]['modTime']}
                orderpass_list.append(info)   
            except:
                pass
              
        return orderpass_list

    def findProjectInf(self, code):
        url_search = 'https://eam.cti-cert.com/purchaseTenderpRice/search.do?txnCode=PURCHASE_APPLYMATERIAL&columnTxnCode=PURCHASE_TENDERPRICE'
        search_date = {"column": "materialCode",
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
            'https://eam.cti-cert.com/formPageForward.do?txnCode=PURCHASE_APPLYMATERIAL&action=save&selectedId=&panelName=PurchaseApplyMaterialPanel&dynamicFormListenersPath=/pages/purchase/purchaseApplyMaterial/dynamicForm_listeners.js&tabId=purchaseApplyMaterialsave&rawTxnCode=PURCHASE_APPLYMATERIAL&printTxnCode=&TABID=purchaseApplyMaterialsave').text
        c1 = ccc.find('applyNo:')
        c2 = ccc.find('jbpmProcessId:')
        applyid = ccc[c1:c2 - 1][ccc[c1:c2 -
                                     1].find("'") + 1:ccc[c1:c2 - 1].rfind("'", 1)]
        applydate = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        return [applyid, applydate]

    def getpostdataframe(self):
        """[{'deptName': '医学-苏州生物临床检验部-苏州生物',
             'deptId': '8a8a81d842c1dc520142c68c061b02c2',
             'goods_list': [{'materialCode': 'WD100402904J0YYYYYY2301C8', 'reNum': '1','name', :'','num':'','type':''}
             ]
        """
        cccc = self.session.post(
            'https://eam.cti-cert.com/storeWarning/search.do?txnCode=STORE_WARNING_SEARCH&_dc=1634176321600').json()
        df = pd.DataFrame(cccc["results"])
        df = df[df['reNum'].astype('int') > 0]
        df = df.reset_index(drop=True)
        df = pd.DataFrame(
            df, columns=['deptName', 'deptId', 'materialCode', 'reNum','name','num','type','lowNum'])
        # data_list = []
        # # 直接截取df列表作为dict需要的内容
        # for i in df.groupby('deptName'):
        #     dict1 = {'deptName': i[0], 'deptId': i[1].iloc[0, 1],
        #              'goods_list': i[1].iloc[:, 2:8].to_dict('records')}
        #     data_list.append(dict1)
        #return data_list
        return df

    def AddOrder1(self,user,data_list,find_order_inf):
        url = 'https://eam.cti-cert.com/purchaseApplyMaterial/sp/submit.do?txnCode=PURCHASE_APPLYMATERIAL_SAVE'
        
        for j in data_list:
            if j['deptName'] == '医学-苏州生物兽医运行部-苏州生物':
                code_list = j['goods_list']
                dd_list = []
                total=0
                for i in code_list:
                    information = self.findProjectInf(i['materialCode'])
                    total += float(i['reNum'])*float(information['newPrice'])
                    dd = {"id": "new_b35168b4d7014d13a4a7964b0a76c0df",
                          "supplierspriceId": "",
                          "materialId": "2c9262ec64c56d590164c59d8f5202f0",
                          "name": information['name'],
                          "sortName": information['sortName'],
                          "matCode": i['materialCode'],
                          "type": information['matType'],
                          "factoryName": "",
                          "mannerPack": "",
                          "cas": "",
                          "partNo": "",
                          "unit": information['unit'],
                          "isTender": 1,
                          "num": i['reNum'],
                          "use": "",
                          "isFirst": 0,
                          "price": information['newPrice'],
                          "bidPrice": 0,
                          "total":  float(i['reNum'])*float(information['newPrice']),
                          "remark": "",
                          "applyStatus": 1,
                          "orderStatus": 1,
                          "claimStatus": 1,
                          "isStandard": "0",
                          "picUrl": "",
                          "brandName": information['brand'],
                          "brandId": "",
                          "useType": 1,
                          "taxRate": information['taxRate'],
                          "reason": "",
                          "itemNo": "",
                          "rdNo": "",
                          "claimUserName": "",
                          "claimUser": "",
                          "claimingTime": '',
                          "claimTime": '',
                          "claimRemark": "",
                          "arrivalDate": '',
                          "arrivalNum": 0,
                          "orderNum": 0,
                          "applyId": "",
                          "budgeId": "",
                          "createTime": '',
                          "status": 0,
                          "createUser": "",
                          "modUser": "",
                          "modTime": ''
                          }
                    
                    dd_list.append(dd)
                data = {
                    'jbpmProcessId': '2c9262ec5cf47bfc015cf6dd413408fe',
                    'taskInstId': '',
                    'ATTACHMENT_TEMP_ID': '',
                    'applyNo': find_order_inf[0],
                    'deptName': j['deptId'],
                    # j['deptName']
                    'total': total,
                    'applyUser': user,
                    'applyDate': find_order_inf[1],
                    'applyClaimUserName': '',
                    'status': 1,
                    'remark': '',
                    'DevUtil-DynamicForm-ext-28_purchaseXZApplyMaterialDetSubGrid_filter-inputEl': '物料编码',
                    'createUser': '',
                    'createTime': '',
                    'modUser': '',
                    'modTime': '',
                    'deptId': j['deptId'],
                    'budgeId': '',
                    'submitDate': '',
                    'budge': '',
                    'purchaseApplyMaterialDetJsonData': json.dumps(dd_list),
                    'budgeYear': '',
                    'id': '',
                    'applyStatus': '',
                    'spLastDate': '',
                    'attachment': '',
                    'applyClaimUserId': '',
                    'hiddenfield-1047-inputEl': '',

                }
                response = self.session.post(
                    url, headers=self.headers, data=data).text
                print(response)


if __name__ == '__main__':
    username = '48502'
    password = '123'
    order = PostDepartmentEam()
    order.login(username, password)
    user = '张铭'
    order.AddOrder( user)