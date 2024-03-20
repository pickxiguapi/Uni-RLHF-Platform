<template>
    <div style="border: 1px solid #ccc;">
        <Toolbar style="border-bottom: 1px solid #ccc" :editor="editor" :defaultConfig="toolbarConfig" :mode="mode" />
        <Editor v-model="html" :defaultConfig="editorConfig" :mode="mode"
            @onCreated="onCreated" />
    </div>
</template>

<script>
import Vue from 'vue';
import { Editor, Toolbar } from '@wangeditor/editor-for-vue';

export default Vue.extend({
    components: { Editor, Toolbar },
    props: {
        value: { // 接收父组件传递的内容
            type: String,
            default: ''
        }
    },
    data() {
        return {
            editor: null,
            editorConfig: {
                placeholder: '请输入内容...'
            }
        };
    },
    watch: {
        value(newVal) {
            // 父组件内容更新时，同步更新编辑器内容
            if (this.editor && newVal !== this.editor.getHtml()) {
                this.editor.setHtml(newVal); // 更新编辑器内容
            }
        },
    },
    methods: {
        onCreated(editor) {
            this.editor = editor;
            this.editor.setHtml(this.value); // 更新编辑器内容
            setInterval(()=>{
                this.$emit('input', this.editor.getHtml())
            },500)

        },
    },
});
</script>
<style src="@wangeditor/editor/dist/css/style.css"></style>
<style scoped></style>