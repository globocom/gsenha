function handleFiles() {
	startRead('pkfile');	
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
  reader.onload = function(evt){ document.getElementById('pk').value = evt.target.result }
  reader.readAsText(readFile);

 }