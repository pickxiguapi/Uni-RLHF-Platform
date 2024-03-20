<template>
    <v-app>
        <div class="main">
            <transition name="fade">
                <v-alert elevation="5" :type="alertType" style="position: absolute; z-index: 999;" v-if="alertMessage">{{
                    alertMessage }}</v-alert>
            </transition>
            <div class="topBar">
                <div style="display: flex; align-items: center;">
                    <div class="logo">
                        <img src="@/assets/UniRLHFLogo.jpg" alt="">
                        <p>Uni-RLHF</p>
                    </div>
                    <div style="font-size: 20px; margin-left: 40px;">
                        <p style="display: inline; color: #888888;" @click="back">Projects /</p>
                        <p style="display: inline; color: #888888;" @click="backTask">{{ taskName }} / </p>label
                    </div>
                </div>
                <div class="topBar-right">
                    <v-menu offset-y>
                        <template v-slot:activator="{ on, attrs }">
                            <img class="avatar" src="../assets/user.svg" v-bind="attrs" v-on="on">
                        </template>
                        <v-list>
                            <v-list-item @click="logout">
                                <v-icon>mdi-logout</v-icon>
                                <div style="margin-left: 10px;">Log Out</div>
                            </v-list-item>
                            <v-list-item @click="openInNewTab(url_doc)">
                                <v-icon>mdi-file-document-alert-outline</v-icon>
                                <div style="margin-left: 10px;">Docs</div>
                            </v-list-item>
                            <v-list-item @click="openInNewTab(url_github)">
                                <v-icon>mdi-github</v-icon>
                                <div style="margin-left: 10px;">GitHub</div>
                            </v-list-item>
                        </v-list>
                    </v-menu>
                </div>
            </div>


            <div class="container" v-if="instruction">
                <div class="table-div">
                    <v-data-table :headers="headers" :items="desserts" item-key="id" class="table"
                        @click:row="handleRowClick">
                        <template v-slot:item.label="{ item }">
                            <v-icon v-if="item.label == 1">mdi-check</v-icon>
                        </template>
                    </v-data-table>
                </div>

                <div class="container-right">
                    <v-expansion-panels style="margin-right:20px;width:auto" v-model="panel" multiple>
                        <v-expansion-panel>
                            <v-expansion-panel-header>Instruction</v-expansion-panel-header>
                            <v-expansion-panel-content>
                                <div style="padding-bottom: 20px;padding-left:20px;padding-right:20px; width: 100%;">
                                    <div v-html="instruction">
                                    </div>
                                </div>
                            </v-expansion-panel-content>
                        </v-expansion-panel>
                    </v-expansion-panels>
                    <div class="container-right-content">
                        <v-card style="margin-right:20px;width:calc(100% - 20px);margin-bottom:20px;margin-top: 20px;">
                            <div
                                style="display: flex; flex-direction: column; align-items: center; width: 100%; margin-bottom: 10px;">
                                <div style="margin-top: 10px;">Query ID: {{ query_id }}</div>
                                <video-player style="width: 80%;margin:0 auto;box-shadow:5px 5px 8px #888888"
                                    class="video-player vjs-custom-skin" ref="videoPlayer" :playsinline="true"
                                    :options="playerOptions"></video-player>
                            </div>
                        </v-card>



                        <!-- <div v-html="videoHTML"></div> -->

                        <div class="middle_item">
                            <v-card v-for="(item, index) in question" :key="index"
                                style="padding-left: 10px;padding-right: 10px; font-size: 20px; margin-bottom: 10px;">
                                <div>Question {{ index + 1 }}: &nbsp;{{ item }}</div>
                                <v-radio-group v-model="radioGroup[index]" class="d-flex" row>
                                    <v-radio v-for="(option, oIndex) in options[index]" :key="oIndex" :label="option"
                                        :value="oIndex"></v-radio>
                                </v-radio-group>
                            </v-card>

                        </div>

                        <div class="button-div">
                            <v-btn class="btn-docs" color="primary" @click="save">Save</v-btn>
                            <v-btn class="btn-docs" color="primary" @click="skip">Skip</v-btn>
                            <v-btn class="btn-docs" color="primary" @click="exit">Exit</v-btn>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </v-app>
</template>
<script>
import axios from 'axios';
import 'video.js/dist/video-js.css';
import { videoPlayer } from 'vue-video-player';

export default {
    data() {
        return {
            url_doc: '',
            url_github: '',
            alertType: 'error',
            alertMessage: '',
            taskID: '',
            taskName: '',
            desserts: [],
            query_id: '',
            url_list: [],
            videoSource: '',
            instruction: '',
            question: [],
            options: [],
            label: '',
            currentIndex: 0,
            radioGroup: [],
            headers: [
                { text: 'ID', align: 'center', sortable: false, value: 'id', },
                { text: '', align: 'center', sortable: false, value: 'label', },
            ],

            playerOptions: {
                playbackRates: [0.7, 1.0, 1.5, 2.0], //播放速度
                autoplay: false, //如果true,浏览器准备好时开始回放。
                muted: false, // 默认情况下将会消除任何音频。
                loop: false, // 导致视频一结束就重新开始。
                preload: 'auto', // 建议浏览器在<video>加载元素后是否应该开始下载视频数据。auto浏览器选择最佳行为,立即开始加载视频（如果浏览器支持）
                language: 'zh-CN',
                aspectRatio: '16:9', // 将播放器置于流畅模式，并在计算播放器的动态大小时使用该值。值应该代表一个比例 - 用冒号分隔的两个数字（例如"16:9"或"4:3"）
                fluid: true, // 当true时，Video.js player将拥有流体大小。换句话说，它将按比例缩放以适应其容器。
                sources: [{
                    type: "video/mp4",
                    src: "" //url地址

                }],
                poster: "", //你的封面地址
                // width: document.documentElement.clientWidth,
                notSupportedMessage: '此视频暂无法播放，请稍后再试', //允许覆盖Video.js无法播放媒体源时显示的默认信息。
                controlBar: {
                    timeDivider: true,
                    durationDisplay: true,
                    remainingTimeDisplay: false,
                    fullscreenToggle: true  //全屏按钮
                }
            },

        }

    },

    computed: {
        player() {
            return this.$refs.videoPlayer.player
        }
    },

    created() {
        this.url_doc = this.$store.state.url_doc
        this.url_github = this.$store.state.url_github
        let user_id = this.$route.query.user_id;
        let query_id_list = this.$route.query.query_id_list;
        this.taskName = this.$route.query.taskName;
        this.taskID = this.$route.query.taskID;
        this.user_id = user_id
        this.query_id_list = query_id_list
        axios.post(this.$store.state.baseUrl + '/labelled_list', {
            user_id: this.user_id,
            query_id_list: this.query_id_list,
        }).
            then((response) => {
                this.labelled_list = response.data.labelled_list
                console.log(this.labelled_list)
                for (let i = 0; i < query_id_list.length; i++) {
                    let item = {}
                    item.id = this.query_id_list[i]
                    item.label = this.labelled_list[i]  //是否已经标注
                    this.desserts.push(item)
                }
                console.log(this.desserts)
            }).catch((e) => {

            })

        axios.post(this.$store.state.baseUrl + '/label_config', {
            project_id: this.taskID,
            user_id: this.user_id,
            query_id_list: this.query_id_list,

        })
            .then((response) => {
                this.$store.commit('setProject_id', this.taskID);
                this.$store.commit('setUser_id', this.user_id);
                this.$store.commit('setQuery_id_list', this.query_id_list);
                this.url_list = response.data.url
                this.instruction = response.data.instruction
                this.question = response.data.question
                this.options = response.data.options
                console.log(this.question, this.options)
                this.feedback_type = response.data.feedback_type
                // 将 videoSource 设置为第一个视频的 URL
                if (this.url_list.length > 0) {
                    this.query_id = this.query_id_list[0];
                    this.videoSource = this.url_list[0];
                    let wierd = this.videoSource.replace("@/assets/video/", "")
                    let video = require('@/assets/video/' + wierd)
                    this.playerOptions.sources[0].src = video
                    this.currentIndex = 0
                }

            })
            .catch((error) => {
                console.error('error:', error);
            });

    },


    methods: {
        handleRowClick(row) {
            this.query_id = row.id;
            this.radioGroup = []
            let index = this.desserts.findIndex(item => item.id === row.id);
            this.videoSource = this.url_list[index]

            let wierd = this.videoSource.replace("@/assets/video/", "")
            let video = require('@/assets/video/' + wierd)
            this.playerOptions.sources[0].src = video
            // console.log(index)   
            // console.log(this.videoSource)   
        },
        save() {
            let currentDate = new Date();
            this.currentTime = currentDate.toLocaleTimeString()

            axios.post(this.$store.state.baseUrl + '/save', {
                user_id: this.user_id,
                query_id: this.query_id,
                feedback_type: this.feedback_type,
                label: this.radioGroup,

            })
                .then((response) => {
                    this.desserts.forEach(dessert => {
                        if (dessert.id == this.query_id) {
                            dessert.label = 1;
                            this.$forceUpdate
                        }
                    });
                    this.$store.commit('User_id', this.user_id);
                    this.$store.commit('Query_id', this.query_id);
                    this.$store.commit('Feedback_type', this.feedback_type);
                    this.$store.commit('Label', this.radioGroup);
                    this.playNextVideo();
                })
                .catch((error) => {
                    console.error('error:', error);
                });



        },
        skip() {
            axios.post(this.$store.state.baseUrl + '/skip', {
                query_id: this.query_id
            })
                .then((response) => {
                    this.$store.commit('Query_id', this.query_id);
                    this.playNextVideo();
                })
                .catch((error) => {
                    console.error('error:', error);
                });
        },
        exit() {
            this.$router.push("/homepage")
        },
        playNextVideo() {
            // 获取下一个视频的索引
            this.currentIndex = this.url_list.indexOf(this.videoSource);
            this.currentIndex = this.currentIndex + 1;
            this.radioGroup = []
            // 检查是否超出索引范围
            if (this.currentIndex < this.url_list.length) {
                console.log(this.videoSource)
                // 设置 videoSource 为下一个视频的 URL
                this.videoSource = this.url_list[this.currentIndex];
                let wierd = this.videoSource.replace("@/assets/video/", "")
                let video = require('@/assets/video/' + wierd)
                this.playerOptions.sources[0].src = video
                this.query_id = this.query_id_list[this.currentIndex];
                console.log(this.currentIndex)

            } else {
                this.alertV('There are no more videos', 'error');
            }
        },
        back() {
            this.$router.push("/homepage")
        },
        backTask() {
            this.$router.push({
                path: '/project',
                query: {
                    id: this.taskID,
                }
            });
        },
        logout() {
            this.$store.commit('setUsername', '');
            // this.$store.commit('setRole', '');
            this.$store.commit('setPassword', '');
            // this.$store.commit('setEmail', '');
            this.$router.push('/')
        },
        openInNewTab(url) {
            window.open(url, '_blank');
        },
        alertV(message, type) {
            this.alertType = type
            this.alertMessage = message
            setTimeout(() => {
                this.alertType = ''
                this.alertMessage = ''
            }, 4000)
        }
    }
}
</script>
<style scoped>
.main {
    background-color: #f9f9f9;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: space-between
}

.topBar {
    z-index: 100;
    position: fixed;
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
    display: flex;
    align-items: center;
}



.avatar {
    height: 30px;
    width: 30px;
    margin-left: 24px;
}

.infoBar {
    position: fixed;
    top: 48px;
    height: 40px;
    width: 100vw;
    background-color: #f3f3f3;
    z-index: 100;
    padding: 0px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.container {
    display: flex;
    width: 100vw;
    margin-top: 50px;
    margin-left: 20px;
    margin-right: 20px;
    max-width: 99999px;
    overflow: hidden;
}

.container-right {
    flex: 5;
    height: 100%;
    overflow-y: auto;
}

.container-right-content {
    width: 100%;
    /* min-height: calc(100% - 80px); */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.middle_item {
    line-height: 40px;
    width: calc(100% - 20px);
    margin-right: 20px;
}



.video-div {
    margin-top: 20px;
    margin-bottom: 20px;
    /* 添加下边距 */
}

.button-div {
    display: flex;
    justify-content: space-around;
    /* 按钮水平排列并均匀分布 */
}

.btn-docs {
    margin: 0 10px;
    /* 按钮间距 */
}

.taskInfo {
    color: rgba(0, 0, 0, 0.6);
}

.table-div {
    flex: 1.5;
    margin-right: 20px;
    /* 添加右边距 */
}

.table {
    height: calc(100vh - 88px);
    width: 100%;
}



.text-overflow-ellipsis {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    width: 15vw;
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity .5s;
}

.fade-enter,
.fade-leave-to {
    opacity: 0;
}</style>