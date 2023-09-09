<template>
	<div id="root">
		<router-view/>
	</div>
</template>

<style lang="scss">
	@import 'stylesheets/main.scss';

	html, body, #root { width: 100%; height: 100%; margin: 0px; padding: 0px; overflow: hidden; }
	#root {
		font-family: $def-font-stack; font-size: 14px;
		-webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
		-webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%;
		color: #ccc; overflow-y: auto;
	}
</style>
