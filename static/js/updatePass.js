function getIdPasswd(id) {
	
	var elem = document.getElementById("passwd"+id);

	var name = document.getElementById("name"+id).getAttribute("passwdname")
	var url = elem.getElementsByClassName('form-group')[1].getElementsByClassName('form-control')[0].value;
	var login = elem.getElementsByClassName('form-group')[2].getElementsByClassName('form-control')[0].value;
	var description = elem.getElementsByClassName('form-group')[3].getElementsByClassName('form-control')[0].childNodes[0].nodeValue;

	var jSON = {"name":name,"id":id,"url":url,"login":login,"description":description};
	var stringJson = JSON.stringify(jSON);

	sessionStorage.id_passwd = stringJson;

	window.location.href = '/update/password';
}

function setIdPasswd() {

	var elem = JSON.parse(sessionStorage.id_passwd);

    var pki = forge.pki;

    privateKey = pki.privateKeyFromPem(sessionStorage.pk);

	document.getElementById('id_passwd').value = elem["id"];
	document.getElementById('url').placeholder = elem["url"];
	document.getElementById('login').placeholder = elem["login"];
	document.getElementById('description').placeholder = DOMPurify.sanitize(privateKey.decrypt(forge.util.decode64(elem["description"]),'RSA-OAEP', {
                    md: forge.md.sha1.create(), mgf1: { md: forge.md.sha1.create() } }));
	document.getElementById('name').placeholder = elem["name"];
	document.getElementById('passwd').placeholder = "**********";
	document.getElementById('passwd2').placeholder = "**********";


}