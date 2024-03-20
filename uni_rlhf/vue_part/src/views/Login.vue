<template>
    <v-app>
        <div class="main">
            <transition name="fade">
                <v-alert elevation="5" :type="alertType" style="position: absolute; z-index: 999;" v-if="alertMessage">{{ alertMessage }}</v-alert>
            </transition>
            <div class="topBar">
                <div class="logo">
                    <img src="@/assets/UniRLHFLogo.jpg" alt="">
                    <p>Uni-RLHF</p>
                </div>
                <div class="topBar-right">
                    <v-btn class="btn-docs" outlined color="blue" @click="openInNewTab(url_doc)">docs</v-btn>
                    <v-btn outlined @click="openInNewTab(url_github)">
                        <v-icon style="margin-right: 5px;">mdi-github</v-icon>GitHub
                    </v-btn>
                </div>
            </div>
            <div class="login">
                <v-tabs color="blue accent-4" centered style="border-radius: 40px;"  v-model="tabIndex">
                    <v-tab>Log in</v-tab>
                    <v-tab>Sign Up</v-tab>
                    <v-tab-item>
                        <v-container fluid style="padding: 60px 15px; border-radius: 24px;"
                            class="d-flex flex-column align-center">
                            <v-text-field dense v-model="username" label="username" outlined color="blue"
                                style="width: 100%;"></v-text-field>
                            <!-- <v-text-field dense v-model="email" label="email" outlined color="blue"
                                style="width: 100%;"></v-text-field> -->
                            <v-text-field dense v-model="password" :type="show1 ? 'text' : 'password'"
                                :append-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'" @click:append="show1 = !show1"
                                label="password" outlined color="blue" style="width: 100%;"></v-text-field>
                            <v-btn color="primary" style="width: 100%;" @click="login">Log In</v-btn>
                        </v-container>
                    </v-tab-item>
                    <v-tab-item>
                        <v-container fluid style="padding: 30px 15px; border-radius: 24px;"
                            class="d-flex flex-column align-center">
                            <v-text-field  dense v-model="username0" label="username" outlined color="blue" style="width: 100%;"></v-text-field>
                            <v-text-field  dense v-model="email0" label="email" outlined color="blue" style="width: 100%;"></v-text-field>
                            <v-text-field  dense v-model="password0" label="password" :type="show2 ? 'text' : 'password'"
                                :append-icon="show2 ? 'mdi-eye' : 'mdi-eye-off'" @click:append="show2 = !show2" outlined
                                color="blue" style="width: 100%;"></v-text-field>
                            <v-btn color="primary" style="width: 100%;" @click="register">Sign Up</v-btn>
                        </v-container>
                    </v-tab-item>
                </v-tabs>
            </div>
            <div class="bottom" >
                <!-- <v-carousel cycle v-model="model" height="102%" show-arrows-on-hover hide-delimiters>
                    <v-carousel-item v-for="(color, i) in colors" :key="color">
                        <v-sheet :color="color" height="100%" tile>
                            <v-row class="fill-height" align="center" justify="center">
                                <div class="text-h2">
                                    Slide {{ i + 1 }}
                                </div>
                            </v-row>
                        </v-sheet>
                    </v-carousel-item>
                </v-carousel> -->
            </div>
        </div>
    </v-app>
</template>
<script>
import axios from 'axios';
export default {
    data() {
        return {
            url_doc: '',
            url_github: '',
            alertType:'error',
            alertMessage:'',
            model: 0,
            colors: [
                'primary',
                'secondary',
                'yellow darken-2',
                'red',
                'orange',
            ],
            items: [
                'annotator',
                'employer'
            ],
            username: '',
            email: '',
            password: '',
            username0: '',
            email0: '',
            password0: '',
            show1: false,
            show2: false,
            tabIndex: 0
        }
    },
    created(){
        this.url_doc = this.$store.state.url_doc
        this.url_github = this.$store.state.url_github
    },
    methods: {
        a() {
        },
        login() {
            axios.post(this.$store.state.baseUrl + '/login', {
                username: this.username,
                password: this.password,
                // email: this.email,
            })
                .then((response) => {
                    console.log(111,response.data.message)
                    if(response.data.message == "user not found"){
                        this.alertV("user not found",'error')
                    }else if(response.data.message == "Invalid username or password"){
                        this.alertV("Invalid username or password",'error')
                    }else{
                        this.$store.commit('setUsername', this.username);
                        this.$store.commit('setPassword', this.password);
                        // this.$store.commit('setEmail', this.email);
                        this.$router.push("/homepage")
                    }
                })
                .catch((error) => {
                    this.alertV(error.response.data.message,'error')
                    console.error('error:', error);
                });
        },
        register() {
            axios.post(this.$store.state.baseUrl + '/register', {
                username: this.username0,
                password: this.password0,
                email: this.email0,
            })
                .then((response) => {
                    if(response.data.message == "Username already exists"){
                        this.alertV("Username already exists",'error')
                    }
                    else if(response.data.message == "Error registering user"){
                        this.alertV("Error registering user",'error')
                    }
                    else{
                        this.$store.commit('setUsername', this.username0);
                        this.$store.commit('setPassword', this.password0);
                        this.$store.commit('setEmail', this.email0);
                        
                        this.alertV('User registered successfully! Please login.','success')
                        this.tabIndex = 0; 
                    }
                })
                .catch((error) => {
                    this.alertV(error.response.data.message,'error')
                    console.error('error:', error);
                });
        },
        openInNewTab(url) {
            window.open(url, '_blank');
        },
        alertV(message,type){
            this.alertType = type
            this.alertMessage = message
            setTimeout(()=>{
                this.alertType = ''
                this.alertMessage = ''
            },4000)
        }
    }
}
</script>
<style scoped>
html {
    overflow-y: hidden;
}

.main {
    background-color: #f9f9f9;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between
}

.topBar {
    background-color: #fff;
    width: 100vw;
    height: 48px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0px 1px 10px 0px rgba(0, 0, 0, 0.2);
}


.logo {
    height: 36px;
    width: 160px;
    margin-left: 24px;
    line-height: 36px;
    display: flex;
    justify-content: center;
    color: #333333;
    font-size: 22px;
    font-weight: 900;
}


.topBar-right {
    height: 36px;
    margin-right: 24px;
}

.btn-docs {
    margin-right: 10px;
}

.login {
    background-color: #fff;
    height: 350px;
    width: 410px;
    padding-left: 10px;
    padding-right: 10px;
    border-radius: 16px;
    box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.1);
}

.bottom {
    height: 150px;
    width: 100vw;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

</style>