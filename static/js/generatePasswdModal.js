function generateButton(){

	var elem = document.getElementsByClassName("form-group");

	var new_elem = document.createElement("BUTTON");
	new_elem.type = "button";
	new_elem.innerHTML = "Gen. Passwd";
	new_elem.title = "Generate Password";
	new_elem.setAttribute("data-toggle","modal");
	new_elem.setAttribute("data-target","#myModal");
	new_elem.className = "btn btn-primary"
	elem[1].appendChild(new_elem);

}

function savePasswd(){
	document.getElementById('passwd').value=document.getElementById('passwd3').value;
	document.getElementById('passwd2').value=document.getElementById('passwd3').value;
}

function addPlaceHolder(){
	try{
		document.getElementById('username').placeholder = "Username from user that the password will be added.";
	}catch(err){}
	try{
		document.getElementById('url').placeholder = "Url associated with password";
	}catch(err){}
	try{
		document.getElementById('login').placeholder = "Login associated with password";
	}catch(err){}
	try{
		document.getElementById('name').placeholder = "Password's name";
	}catch(err){}
	try{
		document.getElementById('description').placeholder = "Password's description";
	}catch(err){}
}

function start(){
	generateButton();
	addPlaceHolder();
}