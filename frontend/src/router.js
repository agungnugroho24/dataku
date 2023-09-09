import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import Data from './views/Data.vue'

Vue.use(Router)

let router = new Router({
	mode: 'history',
	base: process.env.BASE_URL,
	routes: [
		{ path: '/', name: 'home', component: Home },
		{ path: '/:id', name: 'data', component: Data }
	],
	scrollBehavior (to, from, savedPosition) {
		if (savedPosition) {
			return savedPosition
		} else {
			return { x: 0, y: 0 }
		}
	}
})

router.afterEach((to, from) => {
	if (document.getElementById('root')) { document.getElementById('root').scrollTo(0, 0) }
})

export default router;
