function showPassword(id) {
    var e = document.getElementById(id);

    var pki = forge.pki;

    try{
        privateKey = pki.privateKeyFromPem(sessionStorage.pk);
    }
    catch(err){
        
    }

    var password = e.getAttribute("name");
    var url = document.getElementById(id.replace("passwd","url")).value;
    var description = document.getElementById(id.replace("passwd","description")).value;
    var login = document.getElementById(id.replace("passwd","login")).value;

    try{
        var uncrypted = privateKey.decrypt(forge.util.decode64(password),'RSA-OAEP', {
                    md: forge.md.sha1.create(), mgf1: { md: forge.md.sha1.create() } });
    }
    catch(err){
        alert("Failed to decrypt password, inform your private key again.");
        window.location.href = '/privkey';
    }

    var elem = document.getElementById(id.replace("passwd","senha"));
    elem.type = "password"
    elem.value = uncrypted;

    if (url.length == 684)
    {
        var url_uncrypted = privateKey.decrypt(forge.util.decode64(url),'RSA-OAEP', {
                    md: forge.md.sha1.create(), mgf1: { md: forge.md.sha1.create() } });

        var elem = document.getElementById(id.replace("passwd","url"));
        elem.value = DOMPurify.sanitize(url_uncrypted);
    }
    if (description.length == 684)
    {
        var description_uncrypted = privateKey.decrypt(forge.util.decode64(description),'RSA-OAEP', {
                    md: forge.md.sha1.create(), mgf1: { md: forge.md.sha1.create() } });

        var elem = document.getElementById(id.replace("passwd","description"));
        elem.value = DOMPurify.sanitize(description_uncrypted); 
    }
    if (login.length == 684)
    {
        var login_uncrypted = privateKey.decrypt(forge.util.decode64(login),'RSA-OAEP', {
                    md: forge.md.sha1.create(), mgf1: { md: forge.md.sha1.create() } });

        var elem = document.getElementById(id.replace("passwd","login"));
        elem.value = DOMPurify.sanitize(login_uncrypted);
    }

    var x = document.getElementsByClassName("panel panel-primary");
    var i;
    for (i = 0; i < x.length; i++) {
        if(x[i] == e)
        {    
            if(e.style.display == "block")
            {
                x[i].style.display = 'none';
            }
            else 
            {
                x[i].style.display = 'block';
            }
        }
        else
        {
            x[i].style.display = 'none';
        }    
    }
}


function hideShowPass(id){
    var elem = document.getElementById(id.replace("button","senha"));

    var type = elem.type;

    if(type == "password")
    {
        elem.type = "text";
        elem.select();
    }
    else
    {
        elem.type = "password";
    }

}