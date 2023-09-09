import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import VModal from 'vue-js-modal'
import VueSingleSelect from "vue-single-select";
import Paginate from 'vuejs-paginate'

import { library } from '@fortawesome/fontawesome-svg-core'
import { faSearch, faCaretDown, faTimes, faCircleNotch } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

import _ from 'lodash'

library.add( faSearch, faCaretDown, faTimes, faCircleNotch )
Vue.component('font-awesome-icon', FontAwesomeIcon)
Vue.component('vue-single-select', VueSingleSelect)
Vue.component('paginate', Paginate)

Vue.use(require('vue-chartist'))
Vue.use(VModal)

Vue.config.productionTip = false

const requireComponent = require.context('./assets/icons', false, /\w+\.(svg)$/ )
requireComponent.keys().forEach(fileName => {
	const componentConfig	= requireComponent(fileName)
	const componentName		= _.upperFirst(fileName.replace(/^\.\/(.*)\.\w+$/, '$1'))

	Vue.component(componentName, componentConfig.default || componentConfig)
})

new Vue({
	router,
	store,
	render: h => h(App)
}).$mount('#app')
