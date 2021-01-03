function setCurrent(name) {

    console.log('Set current')

    pages = document.querySelectorAll('.nav-link');
	for(var  n=0; n<pages.length; n++) {
	    nav_index = pages[n].getAttribute('nav_index');
	    if (nav_index == name) {
	        pages[n].setAttribute('current', 'yes');
	    } else {
	        pages[n].setAttribute('current', 'no');
	    }
        console.log(nav_index, pages[n].getAttribute('current'));
    }
}
