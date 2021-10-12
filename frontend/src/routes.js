import Home from './views/public/Home.svelte'
import Discordmessage from './views/public/Discordmessage.svelte'
import Signin from './views/public/Signin.svelte'
import Register from './views/public/Register.svelte'
import EditDetails from './views/public/EditDetails.svelte'
import Scrums from './views/public/Scrums.svelte'

const routes = [
  { name: '/tech/:id', component: Discordmessage },
  { name: '/login', component: Signin},
  { name: '/register', component: Register},
  { name: '/edit', component: EditDetails },
  { name: '/scrum/:start/:end', component: Scrums},
  { name: '/:filterType/:value/', component: Home },
]

export { routes }
