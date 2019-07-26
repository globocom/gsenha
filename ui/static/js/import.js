function importPass(id){

	var file = document.getElementById(id).files[0];
	if(file.type == "text/csv")
	{
		Papa.parse(file, {
			complete: function(results) {
				var passwds_list = [];
				for (var i = 1; i < results.data.length; i++) 
				{
					if(results.data[i].length > 1)
					{
						var tmp = {"folder":results.data[i][1],"name":results.data[i][2],"url":results.data[i][3],"login":results.data[i][4],"passwd":results.data[i][5],"description":results.data[i][6]};
						passwds_list.push(tmp);
					}
				}
				var passwds = {"passwds":passwds_list}
				var stringJson = JSON.stringify(passwds);
				var req = new XMLHttpRequest();
				req.onreadystatechange = function() {
   					if (req.readyState == 4) {
						alert(req.responseText);
						window.location.href = '/passwords';
   					}
   				}
   				req.open("POST","https://"+window.location.host+"/import",true);
   				req.setRequestHeader("Content-type", "application/json");
   				req.send(stringJson);
			}
		});
	}
	else if(file.type == "text/xml")
	{
		if(window.DOMParser)
		{
			var parser = new DOMParser();
			var reader = new FileReader();

			reader.onload = function(){
				var xmlDoc = parser.parseFromString(this.result,"text/xml");

				var groups = xmlDoc.getElementsByTagName("group");

				var passwds_list = [];

				for (var i = 0; i < groups.length; i++) 
				{
					if(groups[i].getElementsByTagName("entry")[0] != undefined)
					{	
						for (var j = 0; j < groups[i].getElementsByTagName("entry").length; j++) {
							var dict = {};
	
							tmp_folder = groups[i].getElementsByTagName("title")[0].childNodes[0].nodeValue;
	
							dict["folder"] = tmp_folder;
	
							if(groups[i].getElementsByTagName("entry")[0].getElementsByTagName("title")[0].childNodes[0] != undefined)
							{
								tmp_name = groups[i].getElementsByTagName("entry")[0].getElementsByTagName("title")[0].childNodes[0].nodeValue;
								dict["name"] = tmp_name;
							}
							if(groups[i].getElementsByTagName("entry")[0].getElementsByTagName("password")[0].childNodes[0])
							{
								tmp_passwd = groups[i].getElementsByTagName("entry")[0].getElementsByTagName("password")[0].childNodes[0].nodeValue;
								dict["passwd"] = tmp_passwd;
							}
							
							if(groups[i].getElementsByTagName("entry")[0].getElementsByTagName("username")[0].childNodes[0] != undefined)
							{
								tmp_login = groups[i].getElementsByTagName("entry")[0].getElementsByTagName("username")[0].childNodes[0].nodeValue;
								dict["login"] = tmp_login;
							}else{dict["login"] = ""}
							if(groups[i].getElementsByTagName("entry")[0].getElementsByTagName("url")[0].childNodes[0] != undefined)
							{
								tmp_url = groups[i].getElementsByTagName("entry")[0].getElementsByTagName("url")[0].childNodes[0].nodeValue;
								dict["url"] = tmp_url;
							}else{dict["url"] = ""}
							if(groups[i].getElementsByTagName("entry")[0].getElementsByTagName("comment")[0].childNodes[0] != undefined)
							{
								tmp_description = groups[i].getElementsByTagName("entry")[0].getElementsByTagName("comment")[0].childNodes[0].nodeValue;
								dict["description"] = tmp_description;
							}else{dict["description"] = ""}
	
							passwds_list.push(dict);
						}
					}
				}

				var passwds = {"passwds":passwds_list}
				var stringJson = JSON.stringify(passwds);
				var req = new XMLHttpRequest();
				req.onreadystatechange = function() {
   					if (req.readyState == 4) {
						alert(req.responseText);
						window.location.href = '/passwords';
   					}
   				}
   				req.open("POST","https://"+window.location.host+"/import",true);
   				req.setRequestHeader("Content-type", "application/json");
   				req.send(stringJson);
			}
			reader.readAsText(file);
		}
	}
	else
	{
		alert("Tipo de arquivo não reconhecido.");
	}
}