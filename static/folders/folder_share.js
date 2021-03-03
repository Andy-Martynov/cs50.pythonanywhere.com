document.addEventListener('DOMContentLoaded', function() {
	console.log('LOAD Folder_Share');
	document.querySelectorAll('.add').forEach(el => el.addEventListener('click', addUser));
	document.querySelectorAll('.remove').forEach(el => el.addEventListener('click', removeUser));
});

async function addUser() {
	console.log('Add!', this);
	const fid = this.getAttribute('fid');
	const uid = this.getAttribute('uid');
	const shared_to = document.querySelector('#shared_to');
	const users = document.querySelector('#users');
	let post = {
		folder_id: fid,
		user_id: uid
	};
	console.log(post);
	let response = await fetch('/folders/add_share', {
		method: 'POST',
	    headers: {
        'Content-Type': 'application/json;charset=utf-8'
		},
		body: JSON.stringify(post)
	});
	let result = await response;
	console.log(result.status);
	if (result.status == 200) {
	    this.className = 'remove';
	    this.firstChild.className = "fas fa-arrow-alt-circle-right w3-text-red";
	    this.removeEventListener("click", addUser);
	    this.addEventListener('click', removeUser)
	    shared_to.appendChild(this);
	}
}

async function removeUser() {
	console.log('Remove!', this);
	const fid = this.getAttribute('fid');
	const uid = this.getAttribute('uid');
	const shared_to = document.querySelector('#shared_to');
	const users = document.querySelector('#users');
	let post = {
		folder_id: fid,
		user_id: uid
	};
	console.log(post);
	let response = await fetch('/folders/remove_share', {
		method: 'POST',
	    headers: {
        'Content-Type': 'application/json;charset=utf-8'
		},
		body: JSON.stringify(post)
	});
	let result = await response;
	console.log(result.status);
	if (result.status == 200) {
	    this.className = 'add';
	    this.firstChild.className = "fas fa-arrow-alt-circle-left w3-text-green";
	    this.removeEventListener("click", removeUser);
	    this.addEventListener('click', addUser)
	    users.appendChild(this);
	}
}

