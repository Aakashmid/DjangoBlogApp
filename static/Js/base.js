function showhidecat() {
    let catDiv = document.getElementById('categories');
    if (catDiv.classList.contains('block')) {
        catDiv.classList.remove('block');
        catDiv.classList.add('hidden');
    }
    else if (catDiv.classList.contains('hidden')) {
        catDiv.classList.remove('hidden');
        catDiv.classList.add('block');
    }
}
function hidecatDiv() {
    let catDiv = document.getElementById('categories');
    if (catDiv.classList.contains('block')) {
        catDiv.classList.remove('block');
        catDiv.classList.add('hidden');
    }
}

// hide naviagation
function hide_navigation() {
    var span_close = document.getElementById('close_modals');
    var nav = document.getElementById('navigation_bar');
    var loginform = document.getElementById('login_modal');
    var imageModal = document.getElementsByClassName('image-box')[0];
    if (imageModal) {
        document.getElementsByClassName('image-box')[0].classList.remove('block');
        document.getElementsByClassName('image-box')[0].classList.add('hidden');
    }
    if (nav.classList.contains('-translate-x-0')) {
        nav.classList.remove('-translate-x-0');
        nav.classList.add('translate-x-full');
    }
    if (span_close.classList.contains('block') && loginform.classList.contains('hidden')) {
        span_close.classList.remove('block');
        span_close.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }

}
// show navigation bar
var hamburger = document.querySelector('#hamburger');
hamburger.addEventListener('click', function () {
    var nav = document.getElementById('navigation_bar');
    var span_background = document.getElementById('close_modals');
    if (nav.classList.contains('translate-x-full')) {
        nav.classList.remove('translate-x-full');
        nav.classList.add('-translate-x-0');
    }
    if (span_background.classList.contains('hidden')) {
        span_background.classList.remove('hidden');
        span_background.classList.add('block');
        document.body.classList.add('overflow-hidden');
    }
});


function searchBar_Show() {
    var searchBar = document.getElementById('searchBar');
    if (searchBar.classList.contains('hidden')) {
        searchBar.classList.remove('hidden');
        searchBar.classList.add('block');
        var nav = document.getElementById('navigation_bar');
        nav.scrollIntoView();
     
    }
    else if (searchBar.classList.contains('block')) {
        searchBar.classList.remove('block');
        searchBar.classList.add('hidden');
    }
}

// show login form
function showLogin() {
    var loginform = document.getElementById('login_modal');
    var nav = document.getElementById('navigation_bar');
    var span_background = document.getElementById('close_modals');
    if (loginform.classList.contains('hidden')) {
        loginform.classList.remove('hidden');
        loginform.classList.add('block');
    }
    if (span_background.classList.contains('hidden')) {
        span_background.classList.remove('hidden');
        span_background.classList.add('block');
        document.body.classList.add('overflow-hidden'); //stop scrolling of body when span is displayed
    }

    if (nav.classList.contains('-translate-x-0')) {
        nav.classList.remove('-translate-x-0');
        nav.classList.add('translate-x-full');
    }
}

function closeLoginModal() {
    var loginform = document.getElementById('login_modal');
    var span_close = document.getElementById('close_modals');

    if (loginform.classList.contains('block')) {
        loginform.classList.remove('block');
        loginform.classList.add('hidden');
    }
    if (span_close.classList.contains('block')) {
        span_close.classList.remove('block');
        span_close.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }

}


//  onclick span hide all modals  and also span element
var span_close = document.getElementById('close_modals');
span_close.addEventListener('click', function () {
    var loginform = document.getElementById('login_modal');
    var nav = document.getElementById('navigation_bar');
    if (loginform.classList.contains('block')) {
        loginform.classList.remove('block');
        loginform.classList.add('hidden');
    }
    if (nav.classList.contains('-translate-x-0')) {
        nav.classList.remove('-translate-x-0');
        nav.classList.add('translate-x-full');
    }
    if (span_close.classList.contains('block')) {
        span_close.classList.remove('block');
        span_close.classList.add('hidden');
        document.body.classList.remove('overflow-hidden');
    }
});


// Dissmiss Alert
var alert = document.getElementById('alert');
if (alert) {
    var alert_btn = document.getElementById('dismiss_alert');
    alert_btn.onclick = function () {
        var alert = document.getElementById('alert');
        alert.classList.toggle('hidden');

    }
}


let previews = document.getElementsByClassName('preview');
Array.from(previews).forEach((element) => {
    element.innerHTML = element.innerText;
})

//Show category on hovering or click categoring link

