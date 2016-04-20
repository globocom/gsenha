function generateRandomChar() {

	char_set = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789`˜!@#$%ˆ&*()-_=+[]{}\\|;:/?.>,<"

	if(window.crypto && window.crypto.getRandomValues)
	{
		while(true)
		{
			var buff = new Uint8Array(1);
			window.crypto.getRandomValues(buff);
			if (char_set.indexOf(String.fromCharCode(buff[0])) > -1 ) return String.fromCharCode(buff[0]);
		}
	}
}

function generatePasswd(length){

	passwd = "";

	if(length > 50) { length = 50; }

	for(var i = 0; i<length;i++)
	{
		passwd = passwd + generateRandomChar();
	}

	var elem = document.getElementById('passwd3');
	elem.value = passwd;

}