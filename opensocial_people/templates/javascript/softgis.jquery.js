
{% extends "javascript/softgis_client.commons.js" %}

 
{% block library_specific_block %}

//valid for jquery 6.1
function add_CSRF_token_in_request_header()
{
    $.ajaxPrefilter(function (options, originalOptions, jqXHR) {
            var CSRFverificationToken = getCookie( CSRF_Cookie_Name );
            if (CSRFverificationToken) {
                jqXHR.setRequestHeader("X-CSRFToken", CSRFverificationToken);
            }
    });
}

function checkRegexp( o, regexp ) {
  if ( !( regexp.test( o ) ) ) {
     return false;
  }
  else {
    return true;
 }
}

function validate_email(email_address){
	if (email_address != null && email_address.length > 6){
	  isEmailValid = checkRegexp( email_address, /^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i);
	  if (!isEmailValid){
	    return false;
	  }
	  else {
	    return true;
	  }
	}
	else{
	  return false;
  	}
}

{% for client in softgis_clients %}
    {{ client }}
{% endfor %}

{% endblock %}
