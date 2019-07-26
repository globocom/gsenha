function delIdPasswd(){
	var tmp = sessionStorage.id_passwd;

	if(tmp != "undefined")
	{
		sessionStorage.removeItem("id_passwd");
	}
}