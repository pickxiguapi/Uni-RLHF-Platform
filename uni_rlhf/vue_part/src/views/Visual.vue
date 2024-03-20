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
                    <v-expansion-panels style="margin-right:20px;width:auto;margin-bottom: 0;" v-model="panel" multiple>
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
                                <div class="content">
                                    <img :src="frameImage + '?rand=' + Math.random()" />
                                    <canvas ref="markCanvas" tabindex='0'></canvas>
                                </div>
                                <span style="font-size: 18px;">{{ frameIndex }}</span>
                                <v-slider v-model="frameIndex" :max="images.length" min="0"
                                    style="width: 60%; height: 40px;flex: 0;" @click="click_slider"></v-slider>
                                <div>
                                    <v-btn style="visibility: hidden;margin-right: 20px;">保存</v-btn>
                                    <v-btn style="visibility: hidden;margin-right: 20px;">清空</v-btn>
                                    <v-btn @click="previousImage" icon color="primary"
                                        large><v-icon>mdi-skip-previous</v-icon></v-btn>
                                    <v-btn @click="togglePlayPause" icon color="primary" large><v-icon>{{ isPlaying ?
                                        'mdi-pause' :
                                        'mdi-play' }}</v-icon></v-btn>
                                    <v-btn @click="nextImage" icon color="primary"
                                        large><v-icon>mdi-skip-next</v-icon></v-btn>
                                    <v-btn @click="save_frame" style="margin-left: 20px;" color="primary">保存</v-btn>
                                    <v-btn @click="clear" style="margin-left: 20px;" color="primary">清空</v-btn>
                                </div>
                            </div>
                        </v-card>

                        <div class="middle_item">
                            <v-card style="padding-left: 10px;padding-right: 10px; font-size: 20px; margin-bottom: 10px;"
                                v-for="(item, index) in question">
                                <div>Qustion {{ index + 1 }}: &nbsp;{{ item }}</div>
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
import { draw } from "../draw";
import Vue from 'vue';



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
            currentIndex: 0, //视频序号
            currentIndex_list: [],
            frameImage: '',
            radioGroup: [],
            headers: [
                { text: 'ID', align: 'center', sortable: false, value: 'id', },
                { text: '', align: 'center', sortable: false, value: 'label', },
            ],

            images: [],
            frameIndex: 0,
            isPlaying: false,
            intervalId: null,
            selectedImages: [],

            markList: [],
            length: 0,
            ctx: null,
            canvas: null,
            dataToSend: {}
        }
    },
    mounted() {
        this.initCanvas(); // 画布初始化
        this.$watch(
            () => this.markList,
            (newValue, oldValue) => {
                console.log("!!!!!!!!!!!!!!") // 输出数组长度
                let length = newValue.length
                for (let i = 0; i < length; i++) {
                    console.log(this.markList[i].x, this.markList[i].y, this.markList[i].w, this.markList[i].h)
                }
            }
        );

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
                this.query_length = response.data.query_length
                console.log(this.question, this.options)
                this.feedback_type = response.data.feedback_type

                // 将 videoSource 设置为第一个视频的 URL
                if (this.url_list.length > 0) {
                    this.query_id = this.query_id_list[0];
                    this.videoSource = this.url_list[0];
                    for (let i = 0; i < this.query_length; i++) {
                        this.images.push(this.videoSource + `/${i}.jpg`)
                    }

                    let wierd = this.images[0].replace("@/assets/video/", "")
                    this.frameImage = require('@/assets/video/' + wierd)
                    console.log(this.frameImage)
                }

            })
            .catch((error) => {
                console.error('error:', error);
            });

    },


    methods: {
        click_slider() {
            this.nextImage()
        },
        initCanvas() {
            let that = this
            this.$nextTick(() => {
                // 初始化canvas宽高
                let cav = this.$refs.markCanvas;
                cav.width = '300';
                cav.height = '300';
                this.ctx = cav.getContext('2d');
                this.ctx.strokeStyle = 'blue'
                cav.style.cursor = 'crosshair'
                // 计算使用变量
                let list = this.markList; // 画框数据集合, 用于服务端返回的数据显示和绘制的矩形保存



                // 若服务端保存的为百分比则此处需计算实际座标, 直接使用实际座标可省略
                list.forEach(function (value, index, array) {
                    let newValue = {
                        x: value.x * cav.width,
                        y: value.y * cav.height,
                        w: value.w * cav.width,
                        h: value.h * cav.height,
                    }
                    list.splice(index, 1, newValue)

                })

                // 若list长度不为0, 则显示已标记框
                if (this.length !== 0) {
                    list.forEach(function (value, index, array) {
                        // 遍历绘制所有标记框
                        ctx.rect(value.x, value.y, value.w, value.h);
                        console.log(value.x, value.y, value.w, value.h)
                        ctx.stroke();
                    });
                }

                // 调用封装的绘制方法
                draw(cav, list);

                // 备注: js中对象操作指向的是对象的物理地址, 获取绘制完矩形的结果数组直接取用或处理this.markList即可
            })
        },

        handleRowClick(row) {
            this.images = []
            this.query_id = row.id;
            let index = this.desserts.findIndex(item => item.id === row.id);
            this.videoSource = this.url_list[index]

            for (let i = 0; i < this.query_length; i++) {
                this.images.push(this.videoSource + `/${i}.jpg`)
            }
            let wierd = this.images[0].replace("@/assets/video/", "")
            this.frameImage = require('@/assets/video/' + wierd)
            this.initCanvas()
            this.markList = []
            // console.log(index)   
            // console.log(this.videoSource)   
        },

        save_frame() {
            this.markList.forEach(item => {
                const key = this.frameIndex;
                const values = [item.x, item.y, item.w, item.h];

                if (!this.dataToSend[key]) {
                    this.dataToSend[key] = [values];
                } else {
                    this.dataToSend[key].push(values);
                }
            });

            console.log(this.dataToSend);
            this.nextImage()
        },

        save() {
            let currentDate = new Date();
            this.currentTime = currentDate.toLocaleTimeString()
            axios.post(this.$store.state.baseUrl + '/save', {
                user_id: this.user_id,
                query_id: this.query_id,
                feedback_type: this.feedback_type,
                label: this.dataToSend,

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
        playNextVideo() {
            // 获取下一个视频的索引
            this.currentIndex = this.url_list.indexOf(this.videoSource);
            this.currentIndex = this.currentIndex + 1;

            // 检查是否超出索引范围
            if (this.currentIndex < this.url_list.length) {

                // 设置 videoSource 为下一个视频的 URL
                this.videoSource = this.url_list[this.currentIndex];
                console.log(this.videoSource)
                this.query_id = this.query_id_list[this.currentIndex];

                this.images = []
                this.dataToSend = {}
                this.initCanvas()
                this.markList = []
                this.frameIndex = 0
                for (let i = 0; i < this.query_length; i++) {
                    this.images.push(this.videoSource + `/${i}.jpg`)
                }

                let wierd2 = this.images[0].replace("@/assets/video/", "")
                this.frameImage = require('@/assets/video/' + wierd2)


            } else {
                this.alertV('There are no more videos', 'error');
            }
        },
        exit() {
            this.$router.push("/homepage")
        },
        togglePlayPause() {
            if (this.isPlaying) {
                this.pauseSlideshow();
            } else {
                this.playSlideshow();
            }
            this.isPlaying = !this.isPlaying;
        },
        playSlideshow() {
            this.intervalId = setInterval(() => {
                this.nextImage();
            }, 1000); // 设置图片切换间隔时间，这里设置为1秒，可以根据需要修改
        },
        pauseSlideshow() {
            clearInterval(this.intervalId);
        },
        nextImage() {
            this.frameIndex = (this.frameIndex + 1) % this.images.length;
            this.frameImage = this.images[this.frameIndex]
            let wierd = this.frameImage.replace("@/assets/video/", "")
            this.frameImage = require('@/assets/video/' + wierd)
            console.log(this.frameImage)
            this.initCanvas()
            this.markList = []
            // this.$forceUpdate()
        },
        previousImage() {
            this.frameIndex = (this.frameIndex - 1 + this.images.length) % this.images.length;
            this.frameImage = this.images[this.frameIndex]
            let wierd = this.frameImage.replace("@/assets/video/", "")
            this.frameImage = require('@/assets/video/' + wierd)
        },
        clear() {
            this.initCanvas()
            this.markList = []
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

    },

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
</style>
<style lang='scss' scoped>
.content {
    position: relative;
    width: 100%;
    /* 或者设置固定宽度 */
    max-width: 300px;
    /* 根据需要调整 */
    height: 300px;
    /* 设置高度，根据需要调整 */
    margin-bottom: 10px;
    /* 调整与其他子元素的间距 */
}

.content img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    /* 保持图像比例填充 */
}

.content canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity .5s;
}

.fade-enter,
.fade-leave-to {
    opacity: 0;
}</style>