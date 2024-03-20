<template>
  <router-view />
</template>

<script>
import axios from 'axios';
export default {
  name: 'App',

  data: () => ({
    //
  }),
  created() {
    axios.get(this.$store.state.baseUrl + '/get_default_json')
      .then((r) => {
        console.log(r.data)
        this.$store.commit('setDocUrl', r.data.url_doc);
        this.$store.commit('setGithubUrl', r.data.url_github);
      })
  }
};
</script>
<style>
html {
  overflow: hidden;
  -ms-overflow-style: none;
  /* IE and Edge */
  scrollbar-width: none;
  /* Firefox */
}

html::-webkit-scrollbar {
  display: none;
}
</style>
