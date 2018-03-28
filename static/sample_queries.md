#### Find out the fields in Realtime Dataset
http://eventdata.utdallas.edu/api/fields?api_key=CD75737EF4CAC292EE17B85AAE4B6&datasource=phoenix_rt
#### Select targets, events and url to where source is North Korea.
http://eventdata.utdallas.edu/api/data?api_key=CD75737EF4CAC292EE17B85AAE4B6&query={"source":{"$in":["PRK","PRKGOV"]}}&select=code,target,url
#### Select source and article url who made public statements (event rootcode = "01") about United States on March 28, 2018.
http://eventdata.utdallas.edu/api/data?api_key=CD75737EF4CAC292EE17B85AAE4B6&query={"target":{"$in":["USA","USAGOV"]},"root_code":"01","date8":"20180328"}&select=code,source,url
#### Find events with CAMEO code 010 and happened in Europe (approximately done using longitude and latitude values)
http://eventdata.utdallas.edu/api/data?api_key=CD75737EF4CAC292EE17B85AAE4B6&datasource=phoenix_rt&query={"code":"010","latitude":{"$gt":36.0,"$lt":70.0},"longitude":{"$gt":-15.0,"$lt":60.0}}&select=geoname,source,target
#### Find events that happened in France.
http://eventdata.utdallas.edu/api/data?api_key=CD75737EF4CAC292EE17B85AAE4B6&query={"geoname":{"$regex":".*France.*"}}&select=code,source,target,url,geoname
#### Find events that happened between March 21 and 28, 2018 and internal to QATAR.
http://eventdata.utdallas.edu/api/data?api_key=CD75737EF4CAC292EE17B85AAE4B6&query={"target":{"$in":["QAT","QATGOV"]},"source":{"$in":["QAT","QATGOV"]},"date8":{"$lt":"20180328","$gt":"20180320"}}&select=code,source,target,url,geoname,date8



