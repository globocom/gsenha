function processLargeArray(passwds) {
    // set this to whatever number of items you can process at once
    var pki = forge.pki;
    privateKey = pki.privateKeyFromPem(sessionStorage.pk);

    publicKey = pki.publicKeyFromPem(document.getElementById('key').value)
 	var progressBar = document.getElementById('progress');

 	barLength = passwds.length

    var chunk = 1;
    var index = 0;

    function doChunk() {
        var cnt = chunk;
        while (cnt-- && index < passwds.length) {
 			var i2 = index+1
 			percent = i2/barLength * 100;
 			percent_s = percent.toString();
 			progressBar.style.width = percent_s.split(".")[0] + "%";
 			progressBar.innerHTML = percent_s.split(".")[0] + "%";
 			progressBar.setAttribute("aria-valuenow",percent_s.split(".")[0]+"%");

            try
            {   	
 			    passwd_tmp = privateKey.decrypt(forge.util.decode64(passwds[index]["passwd"]),'RSA-OAEP', {
                    md: forge.md.sha1.create(), mgf1: { md: forge.md.sha1.create() } });

                description_tmp = privateKey.decrypt(forge.util.decode64(passwds[index]["description"]),'RSA-OAEP', {
                    md: forge.md.sha1.create(), mgf1: { md: forge.md.sha1.create() } });                

                url_tmp = privateKey.decrypt(forge.util.decode64(passwds[index]["url"]),'RSA-OAEP', {
                    md: forge.md.sha1.create(), mgf1: { md: forge.md.sha1.create() } });

                login_tmp = privateKey.decrypt(forge.util.decode64(passwds[index]["login"]),'RSA-OAEP', {
                    md: forge.md.sha1.create(), mgf1: { md: forge.md.sha1.create() } });
            }
            catch(err){
                alert("Failed to decrypt password, inform your private key and try to unlock again.");
                window.location.href = '/privkey';                
            }

 			passwds[index]["passwd"] = forge.util.encode64(publicKey.encrypt(passwd_tmp, "RSA-OAEP", { md: forge.md.sha1.create(),
                                                        mgf1: { md: forge.md.sha1.create() } }));

            passwds[index]["description"] = forge.util.encode64(publicKey.encrypt(description_tmp,"RSA-OAEP", { md: forge.md.sha1.create(),
                                                        mgf1: { md: forge.md.sha1.create() } }));

            passwds[index]["url"] = forge.util.encode64(publicKey.encrypt(url_tmp,"RSA-OAEP", { md: forge.md.sha1.create(),
                                                        mgf1: { md: forge.md.sha1.create() } }));

            passwds[index]["login"] = forge.util.encode64(publicKey.encrypt(login_tmp,"RSA-OAEP", { md: forge.md.sha1.create(),
                                                        mgf1: { md: forge.md.sha1.create() } }));

            if (atob(passwds[index]["passwd"]).length != 512)
            {
                passwds[index]["passwd"] = publicKey.encrypt(passwd_tmp,"RSA-OAEP");
            }
            if (atob(passwds[index]["description"]).length != 512)
            {
                passwds[index]["description"] = publicKey.encrypt(description_tmp,"RSA-OAEP");
            }
            if (atob(passwds[index]["url"]).length != 512)
            {
                passwds[index]["url"] = publicKey.encrypt(url_tmp,"RSA-OAEP");
            }
            if (atob(passwds[index]["login"]).length != 512)
            {
                passwds[index]["login"] = publicKey.encrypt(login_tmp,"RSA-OAEP");
            }

            if (passwds[index]["passwd"].length != 684 || passwds[index]["description"].length != 684 || passwds[index]["url"].length != 684 || passwds[index]["login"].length != 684)
            {
                alert("Something went wrong while unlocking, please try again.");
                window.location.href = '/unlock';
            }
            ++index;
        }
        if (index < passwds.length) {  
         	setTimeout(doChunk, 2);			
        }
        if (index == passwds.length ) { callback(passwds); };
    }
    doChunk();
}

function unlock(passwds,token,user,group){

 	passwds = passwds.replace(/\'/g,"\"")
 	passwds = JSON.parse(passwds)

	processLargeArray(passwds);

 }

function callback(passwds){
	jSON = {"passwords":passwds,"token":token,"usertounlock":user,"group":group};
	sendJson(jSON);
}

 function sendJson (json) {
  	var stringJson = JSON.stringify(json);
	var req = new XMLHttpRequest();

	req.onreadystatechange = function() {
    	if (req.readyState == 4) {
    		if (req.responseText == "error") { window.location.href = "/unlock"; };
    		window.location.href = "/passwords";
		}
	}
	req.open("PUT","https://"+window.location.host+"/unlock",true);

	req.setRequestHeader("Content-type", "application/json");
	req.send(stringJson);
 }