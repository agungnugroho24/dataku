<template lang="html">
	<modal :id="modalName" :name="modalName" transition="pop-out" :width="1000" :height="'auto'" :pivotY=".35" @opened="opened" @before-open="beforeOpen">
		<div class="close-button cursor-pointer" @click="$modal.hide(modalName)">
			<font-awesome-icon icon="times" />
		</div>

		<div id="title">{{ title }}</div>
		<div class="chart-wrapper">
			<D3Map v-if="mapdata.length > 0" :data="mapdata"></D3Map>
		</div>
	</modal>
</template>

<script>
	import axios from 'axios'
	import D3Map from '@/components/D3Map.vue'

	export default {
		data: () => ({
			modalName: "modal-map",
			title: "",
			mapdata: [],
		}),
		methods: {
			opened: function (event) {  },
			beforeOpen: function(event) {
				const { title, id, variable, ...rest }	= event.params;

				this.title		= title;
				this.mapdata	= [];
				axios.get(this.$store.state.baseURL + 'map/' + id, { params: { variable } })
					.then(response => { this.mapdata = response.data[0].data; })
					.catch(err => { console.error(err.response); })
			},
		},
		components: { D3Map }
	}
</script>

<style lang="scss">
	div.v--modal {

	}
</style>
