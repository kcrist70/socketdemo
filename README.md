# LogSocket

##数据到来：
1.server 判断有没有在本地字典
>没有
>>添加进字典
>>>活跃用户：
>>>>有没有在活跃用户appid_dau_date集合：
>>>>>没有
>>>>>>添加本地appid_dau_date集合
>>>>>>增量当天appid_DAU_date 数据增量 +1
>>>>>>增量当天全部用户DAU_date
>>>>>>判断新增用户：
>>>>>>>有没有在all_uv中：
>>>>>>>>有
>>>>>>>>>此处省略为一步： 直接添加，不管有没有
>>>>>>>>>有没有在appid_uv中
>>>>>>>>>>没有：
>>>>>>>>>>>添加进appid_uv中
>>>>>>>>>>有：
>>>>>>>>>>>pass
>>>>>>>>没有（其他）
>>>>>>>>>有没有在appid_uv中（直接添加，根据返回值判断）
>>>>>>>>>>没有
>>>>>>>>>>>添加进appid_nuv_date中
>>>>>>>>>>>添加计数 全部ALL_UV
>>>>>>>>>>>添加计数 单个appid_UV
>>>>>>>>>>>添加计数 当天单个appid_UV_date
>>>>>>>>>>>添加计数 当天全量
>>>>>>>>>>有
>>>>>>>>>>>pass

>>>>>有：
>>>>>>新增用户取消判断

>有：
>>活跃用户：
>>>pass
>>新增用户：
>>>pass
				
				
2.记录数值类型：
+ 当天新增单个uv  
	NUV_APPID_NAME  
	appid_NUV_date  
+	当天新增全部uv  
	NUV_ALL_NAME  
	NUV_date  
+	当天活跃单个UV  
	DAU_APPID_NAME  
	appid_DAU_date  
+	当天活跃全部uv  
	DAU_ALL_NAME  
	DAU_date  
+	全部注册用户：  
	ALL_NAME  
	ALL_UV  
+	单个注册用户：  
	APPID_NAME  			appid_UV  

3.记录集合类型：  
+	当天新增单个uv  
	NUV_APPID_NAME  		
	appid_NUV_date  
+	当天活跃用户集合：  
	DAU_APPID_NAME  		
	appid_DAU_date  
+	用户注册集合  
	APPID_NAME	  		
	appid_UV  