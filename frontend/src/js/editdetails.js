import Nav from '../../views/public/Nav.svelte';
import FootNote from '../../views/public/FootNote.svelte';
import { navigate } from 'svelte-routing';
import { auth } from '../../utils/auth.ts';
import { toasts, ToastContainer, FlatToast } from 'svelte-toasts';
import config from '../../../env';
import { axiosInstance } from '../../utils/axios.ts';
let user = { name: '', rollno:'', discordHandle: '', batch:''}
let inProgress = false
let error = null
import { onMount } from 'svelte';

onMount(async () => {
    let token = localStorage.getItem('token');
    if(token == null)
      window.location.href = '/login';
    const resp = await fetch(`${config.backendurl}/api/members/me/`, {
        headers: {
            'Authorization': 'Bearer ' + token
        }
    }).catch(err => {
        error = "Server error, try again later";
    });
    const userDetails = await resp.json();
    const {name, rollno, discordHandle, batch} = userDetails.data.member;
    user.name = name;
    user.rollno = rollno;
    user.batch = batch;
    user.discordHandle = discordHandle;
    console.log(userDetails);
});

async function save () {
    inProgress = true;
    let token = localStorage.getItem('token');
    if(token == null)
      window.location.href = '/login';
    console.log(user);
    axiosInstance({
        method: 'put',
        url: `${config.backendurl}/api/members/me`,
        data: user,
        headers: { 'Authorization': 'Bearer ' + token }
    })
    .then(response => {
        toasts.add({
            title: 'Success',
            description: 'Update details successful',
            duration: 5000,
            placement: 'bottom-right',
            type: 'success',
            showProgress: true
        });
        inProgress = false;
        error = null;
    })
    .catch(err => {
        let error = 'Update details failed! Please match the required format';
        inProgress = false;
        toasts.add({
            title: 'Oops',
            description: error,
            duration: 5000,
            placement: 'bottom-right',
            type: 'error',
            showProgress: true
        });
    }); 
}
