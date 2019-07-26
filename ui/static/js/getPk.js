function storePk(id) {
    var privkey = document.getElementById(id);
    if(privkey.value)
    {
	    sessionStorage.pk = privkey.value;
    }
    else
    {
    	startRead('pkfile')
    }
}

function storePk2(id) {
    var privkey = document.getElementById(id);
    if(privkey.value)
    {
	    sessionStorage.pk = privkey.value;
    }
    else
    {
    	startRead('pkfile')
    }
    window.location.href = '/passwords';
}

function startRead(id) {    
  var file = document.getElementById(id).files[0];
  var pk;
  if(file){
    getAsText(file);
  }
}

function getAsText(readFile) {
        
  var reader = new FileReader();
  reader.onload = function(evt){ sessionStorage.pk = evt.target.result }
  reader.readAsText(readFile);

 }