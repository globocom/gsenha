function check_clipboard() {

	var teste = typeof(document.execCommand('copy'));
	if(teste == "boolean") 
	{
		var elem = document.getElementsByName("clip");
		for (var i = 0; i < elem.length; i++) {

			var new_elem_ext = document.createElement("SPAN");
			var new_elem_int = document.createElement("SPAN");

			new_elem_int.className = "glyphicon glyphicon-circle-arrow-up";
			new_elem_ext.className = "input-group-addon pointer copy-to-clipboard";
			new_elem_ext.title = "copied to clipboard";
			new_id = elem[i].id;
			new_elem_ext.id = new_id.replace("clip","copy");
			new_elem_ext.setAttribute("onClick", "copyToClipboard('"+new_elem_ext.id+"');");

			new_elem_ext.setAttribute("data-toggle", "tooltip");
			new_elem_ext.setAttribute("data-placement", "bottom");
			new_elem_ext.setAttribute("data-trigger", "click");
	
			new_elem_ext.appendChild(new_elem_int);
			elem[i].appendChild(new_elem_ext);

		}

		$('.copy-to-clipboard').tooltip('hide');
		$('.copy-to-clipboard').on('click', function(){
			setTimeout(function(){
				$('.copy-to-clipboard').tooltip('hide');
			}, 1000);
		});
	}
}

function copyToClipboard(id)
{ 
   	var elem = document.getElementById(id.replace("copy","senha"));
   	elem.type = "text";
   	elem.select();
   	document.execCommand('copy');
   	elem.type = "password";
}