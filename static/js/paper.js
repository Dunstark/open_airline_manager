/**
 * Copyright 2015 Thomas Seguin. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function() {
    $(".paper-input").focusin(function( event ){
        $(this).siblings(".paper-label").addClass("focused");
        $(this).parent().addClass("focused");
    });
    $(".paper-input").focusout(function( event ){
        $(this).siblings(".paper-label").removeClass("focused");
        $(this).parent().removeClass("focused");
    });

});

showToast = function(text) {
  $("#paper-toast").children(".paper-toast-content").text(text);
  $("#paper-toast").removeClass("hidden");
  setTimeout(toastTransition, 0.2);
}

toastTransition = function() {
  $("#paper-toast").removeClass("paper-toast-hidden");
  setTimeout(hideToast, 2.2);
}

hideToast = function(text) {
  $("#paper-toast").addClass("paper-toast-hidden");
  setTimeout(hideToastFinal, 0.2);
}

hideToastFinal = function() {
  $("#paper-toast").addClass("hidden");
}