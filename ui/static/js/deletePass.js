function deletePass(id){

	if(confirm("Do you realy want to delete this password?") == true)
	{

		var req = new XMLHttpRequest();

		req.onreadystatechange = function() {
    		if (req.readyState == 4) {
				location.reload();
    		}
		}

		req.open("DELETE","https://"+window.location.host+"/delete/password/"+id,true);
		req.send();
	}
}