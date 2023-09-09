<template lang="html">
	<modal :id="modalName" :name="modalName" transition="pop-out" :width="1000" :height="'auto'" :pivotY=".35" @opened="opened" @before-open="beforeOpen">
		<div class="close-button cursor-pointer" @click="$modal.hide(modalName)">
			<font-awesome-icon icon="times" />
		</div>

		<div id="title">{{ title }}</div>
		<div id="table-wrapper" v-html="html"></div>
	</modal>
</template>

<script>
	import axios from 'axios'

	export default {
		data: () => ({
			modalName: "modal-table",
			title: "",
			html: "",
		}),
		methods: {
			opened: function (event) {  },
			beforeOpen: function(event) {
				this.title	= event.params.title;
				this.html	= "";
				axios.get(this.$store.state.baseURL + 'table/' + event.params.id)
					.then(response => { this.html = response.data; })
					.catch(err => { console.error(err.response); })

			},
		},
	}
</script>

<style lang="scss">
	div.v--modal {
		overflow: visible!important;

		#table-wrapper {
			overflow: auto; max-height: 500px; color: black;
			table {
				border: none; border-spacing: 0px; table-layout: auto; width: 100%;
				tr { border: none; }
				thead th { text-align: center; }
				tbody th { text-align: center; }
				tbody td { padding: 5px; }
			}
		}
	}
</style>
