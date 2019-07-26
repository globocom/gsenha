function exportPasswd(){
    if(confirm("You are about to export all your passwords in clear text, do you realy want to continue?") == true)
    {
        var saveData = (function (){
            var a = document.createElement("a");
            document.body.appendChild(a);
            a.style = "display: none";
            return function (data, fileName) {
                var blob = new Blob([data], {type: "text/csv"}),
                    url = window.URL.createObjectURL(blob);
                a.href = url;
                a.download = fileName;
                a.click();
                window.URL.revokeObjectURL(url);
            };
        }());

        
        var elems = document.getElementById('senhas pessoais').getElementsByClassName("panel panel-primary");
    
        var text = "uuid,group,title,url,user,password,notes\n"

        var decrypt = new JSEncrypt();
        decrypt.setPrivateKey(sessionStorage.pk);
    
        for (var i = 0; i < elems.length; i++) {
            passwd_tmp = elems[i].getAttribute("name");
            passwd = decrypt.decrypt(passwd_tmp);
            name = elems[i].getElementsByClassName("panel-heading")[0].childNodes[0].nodeValue;

            url = elems[i].getElementsByClassName("panel-body")[0].getElementsByClassName("form-group")[1].childNodes[3].value;
            if (url.length == 684)
            {
                url = decrypt.decrypt(url);
            }
            login = elems[i].getElementsByClassName("panel-body")[0].getElementsByClassName("form-group")[2].childNodes[3].value;
            if (login.length == 684)
            {
                login = decrypt.decrypt(login);
            }
            description = elems[i].getElementsByClassName("panel-body")[0].getElementsByClassName("form-group")[3].childNodes[3].value;
            if (description.length == 684)
            {
                description = decrypt.decrypt(description);
            }
    
            text = text+",,"+name+","+url+","+login+","+passwd+","+description+"\n";
        }
    
        
        var fileName = "senhas.csv";
        
        saveData(text,fileName)
    }
}