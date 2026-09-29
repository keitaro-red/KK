import { createHotContext as __vite__createHotContext } from "/@vite/client";import.meta.hot = __vite__createHotContext("/src/components/chat/ChatSidebar.vue");import { ref } from "/node_modules/.vite/deps/vue.js?v=e87a745c"
import { Plus, Expand, Fold } from "/node_modules/.vite/deps/@element-plus_icons-vue.js?v=e87a745c"
import ConversationList from "/src/components/chat/ConversationList.vue"


const _sfc_main = {
  __name: 'ChatSidebar',
  props: {conversations:Array,currentThreadId:String},
  emits: ['new','select'],
  setup(__props, { expose: __expose }) {
  __expose();




const collapsed = ref(false)

const __returned__ = { collapsed, ref, get Plus() { return Plus }, get Expand() { return Expand }, get Fold() { return Fold }, ConversationList }
Object.defineProperty(__returned__, '__isScriptSetup', { enumerable: false, value: true })
return __returned__
}

}
import { createVNode as _createVNode, resolveComponent as _resolveComponent, withCtx as _withCtx, createTextVNode as _createTextVNode, openBlock as _openBlock, createBlock as _createBlock, createCommentVNode as _createCommentVNode, createElementVNode as _createElementVNode, vShow as _vShow, withDirectives as _withDirectives, normalizeClass as _normalizeClass, createElementBlock as _createElementBlock } from "/node_modules/.vite/deps/vue.js?v=e87a745c"

const _hoisted_1 = { class: "chat-sidebar_head" }

function _sfc_render(_ctx, _cache, $props, $setup, $data, $options) {
  const _component_el_icon = _resolveComponent("el-icon")
  const _component_el_button = _resolveComponent("el-button")

  return (_openBlock(), _createElementBlock("aside", {
    class: _normalizeClass(["chat-sidebar", {'is_collapsed':$setup.collapsed}])
  }, [
    _createElementVNode("div", _hoisted_1, [
      (!$setup.collapsed)
        ? (_openBlock(), _createBlock(_component_el_button, {
            key: 0,
            class: "chat-sidebar_new",
            onClick: _cache[0] || (_cache[0] = $event => (_ctx.$emit('new')))
          }, {
            default: _withCtx(() => [
              _createVNode(_component_el_icon, null, {
                default: _withCtx(() => [
                  _createVNode($setup["Plus"])
                ]),
                _: 1 /* STABLE */
              }),
              _cache[3] || (_cache[3] = _createTextVNode(" 新对话 ", -1 /* CACHED */))
            ]),
            _: 1 /* STABLE */
          }))
        : _createCommentVNode("v-if", true),
      _createVNode(_component_el_button, {
        class: "chat-sidebar_toggle",
        text: "",
        onClick: _cache[1] || (_cache[1] = $event => ($setup.collapsed = !$setup.collapsed))
      }, {
        default: _withCtx(() => [
          (!$setup.collapsed)
            ? (_openBlock(), _createBlock(_component_el_icon, { key: 0 }, {
                default: _withCtx(() => [
                  _createVNode($setup["Expand"])
                ]),
                _: 1 /* STABLE */
              }))
            : (_openBlock(), _createBlock(_component_el_icon, { key: 1 }, {
                default: _withCtx(() => [
                  _createVNode($setup["Fold"])
                ]),
                _: 1 /* STABLE */
              }))
        ]),
        _: 1 /* STABLE */
      })
    ]),
    _withDirectives(_createVNode($setup["ConversationList"], {
      conversations: $props.conversations,
      "current-thread-id": $props.currentThreadId,
      onSelect: _cache[2] || (_cache[2] = $event => (_ctx.$emit('select', $event)))
    }, null, 8 /* PROPS */, ["conversations", "current-thread-id"]), [
      [_vShow, !$setup.collapsed]
    ])
  ], 2 /* CLASS */))
}


import "/src/components/chat/ChatSidebar.vue?t=1790181251059&vue&type=style&index=0&scoped=5615bdbe&lang.css"

_sfc_main.__hmrId = "5615bdbe"
typeof __VUE_HMR_RUNTIME__ !== 'undefined' && __VUE_HMR_RUNTIME__.createRecord(_sfc_main.__hmrId, _sfc_main)
import.meta.hot.on('file-changed', ({ file }) => {
  __VUE_HMR_RUNTIME__.CHANGED_FILE = file
})
import.meta.hot.accept(mod => {
  if (!mod) return
  const { default: updated, _rerender_only } = mod
  if (_rerender_only) {
    __VUE_HMR_RUNTIME__.rerender(updated.__hmrId, updated.render)
  } else {
    __VUE_HMR_RUNTIME__.reload(updated.__hmrId, updated)
  }
})
import _export_sfc from "/@id/__x00__plugin-vue:export-helper"
export default /*#__PURE__*/_export_sfc(_sfc_main, [['render',_sfc_render],['__scopeId',"data-v-5615bdbe"],['__file',"/app/src/components/chat/ChatSidebar.vue"]])
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJuYW1lcyI6W10sInNvdXJjZXMiOlsiQ2hhdFNpZGViYXIudnVlIl0sInNvdXJjZXNDb250ZW50IjpbIuWvueivneS+p+i+ueagj1xyXG48dGVtcGxhdGU+XHJcbiAgICA8YXNpZGUgY2xhc3M9XCJjaGF0LXNpZGViYXJcIiA6Y2xhc3M9XCJ7J2lzX2NvbGxhcHNlZCc6Y29sbGFwc2VkfVwiPlxyXG4gICAgICAgIDxkaXYgY2xhc3M9XCJjaGF0LXNpZGViYXJfaGVhZFwiPlxyXG4gICAgICAgICAgICA8ZWwtYnV0dG9uXHJcbiAgICAgICAgICAgICAgICBjbGFzcz1cImNoYXQtc2lkZWJhcl9uZXdcIlxyXG4gICAgICAgICAgICAgICAgdi1pZj1cIiFjb2xsYXBzZWRcIlxyXG4gICAgICAgICAgICAgICAgQGNsaWNrPVwiJGVtaXQoJ25ldycpXCJcclxuICAgICAgICAgICAgPlxyXG4gICAgICAgICAgICAgICAgPGVsLWljb24+PFBsdXMgLz48L2VsLWljb24+XHJcbiAgICAgICAgICAgICAgICDmlrDlr7nor51cclxuICAgICAgICAgICAgPC9lbC1idXR0b24+XHJcbiAgICAgICAgICAgIDxlbC1idXR0b25cclxuICAgICAgICAgICAgICAgIGNsYXNzPVwiY2hhdC1zaWRlYmFyX3RvZ2dsZVwiXHJcbiAgICAgICAgICAgICAgICB0ZXh0XHJcbiAgICAgICAgICAgICAgICBAY2xpY2s9XCJjb2xsYXBzZWQgPSAhY29sbGFwc2VkXCJcclxuICAgICAgICAgICAgPlxyXG4gICAgICAgICAgICAgICAgPGVsLWljb24gdi1pZj1cIiFjb2xsYXBzZWRcIj48RXhwYW5kIC8+PC9lbC1pY29uPlxyXG4gICAgICAgICAgICAgICAgPGVsLWljb24gdi1lbHNlPjxGb2xkIC8+PC9lbC1pY29uPlxyXG4gICAgICAgICAgICA8L2VsLWJ1dHRvbj5cclxuICAgICAgICA8L2Rpdj5cclxuXHJcbiAgICAgICAgPENvbnZlcnNhdGlvbkxpc3RcclxuICAgICAgICAgICAgdi1zaG93PVwiIWNvbGxhcHNlZFwiXHJcbiAgICAgICAgICAgIDpjb252ZXJzYXRpb25zPVwiY29udmVyc2F0aW9uc1wiXHJcbiAgICAgICAgICAgIDpjdXJyZW50LXRocmVhZC1pZD1cImN1cnJlbnRUaHJlYWRJZFwiXHJcbiAgICAgICAgICAgIEBzZWxlY3Q9XCIkZW1pdCgnc2VsZWN0JywgJGV2ZW50KVwiXHJcbiAgICAgICAgLz5cclxuICAgIDwvYXNpZGU+XHJcbjwvdGVtcGxhdGU+XHJcblxyXG48c2NyaXB0IHNldHVwPlxyXG5pbXBvcnQgeyByZWYgfSBmcm9tICd2dWUnXHJcbmltcG9ydCB7IFBsdXMsIEV4cGFuZCwgRm9sZCB9IGZyb20gJ0BlbGVtZW50LXBsdXMvaWNvbnMtdnVlJ1xyXG5pbXBvcnQgQ29udmVyc2F0aW9uTGlzdCBmcm9tICcuL0NvbnZlcnNhdGlvbkxpc3QudnVlJ1xyXG5cclxuZGVmaW5lUHJvcHMoe2NvbnZlcnNhdGlvbnM6QXJyYXksY3VycmVudFRocmVhZElkOlN0cmluZ30pXHJcbmRlZmluZUVtaXRzKFsnbmV3Jywnc2VsZWN0J10pXHJcblxyXG5jb25zdCBjb2xsYXBzZWQgPSByZWYoZmFsc2UpXHJcbjwvc2NyaXB0PlxyXG5cclxuPHN0eWxlIHNjb3BlZD5cclxuLmNoYXQtc2lkZWJhciB7XHJcbiAgICB3aWR0aDogMjAwcHg7XHJcbiAgICBkaXNwbGF5OiBmbGV4O1xyXG4gICAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjtcclxuICAgIGJhY2tncm91bmQ6dmFyKC0ta2stYmctc2lkZWJhcik7XHJcbiAgICB0cmFuc2l0aW9uOndpZHRoIDAuMnMgZWFzZTtcclxufVxyXG4uY2hhdC1zaWRlYmFyLmlzX2NvbGxhcHNlZCB7XHJcbiAgICB3aWR0aDogNDhweDtcclxufVxyXG5cclxuLmNoYXQtc2lkZWJhciB7XHJcbiAgICBib3JkZXItcmlnaHQ6IDJweCBzb2xpZCAjZTNkODk0O1xyXG4gICAgcGFkZGluZzogMTZweCAxMnB4O1xyXG4gICAgZ2FwOiAxMnB4O1xyXG59XHJcblxyXG4uY2hhdC1zaWRlYmFyX19oZWFkIHtcclxuICAgIGRpc3BsYXk6IGZsZXg7XHJcbiAgICBhbGlnbi1pdGVtczogYmV0d2VlbjtcclxuICAgIGdhcDogNnB4O1xyXG4gICAgXHJcbn1cclxuXHJcbi5jaGF0LXNpZGViYXJfbmV3IHtcclxuICAgIHBhZGRpbmc6IDhweDtcclxuICAgIGJhY2tncm91bmQ6ICNkM2M3ODI7XHJcbiAgICBjb2xvcjogd2hpdGU7XHJcbiAgICBib3JkZXI6IDJweCBzb2xpZCAjZTNkODk0O1xyXG4gICAgY3Vyc29yOiBwb2ludGVyO1xyXG59XHJcblxyXG4uY2hhdC1zaWRlYmFyX25ldzpob3ZlciB7XHJcbiAgICBiYWNrZ3JvdW5kOiAjZjVlY2I3O1xyXG59XHJcblxyXG4uY2hhdC1zaWRlYmFyX190b2dnbGUge1xyXG4gICAgLyogdGV4dCDmjInpkq7vvJrljrvmjonovrnmoYbvvIzlj6rnlZnlm77moIcgKi9cclxuICAgIGNvbG9yOndoaXRlO1xyXG4gICAgYmFja2dyb3VuZDogdmFyKC0ta2stcHJpbWFyeSk7XHJcbiAgICAtLWVsLWJ1dHRvbi10ZXh0LWNvbG9yOiB2YXIoLS1ray1wcmltYXJ5KTtcclxuICAgIC0tZWwtYnV0dG9uLWhvdmVyLXRleHQtY29sb3I6IHZhcigtLWtrLXByaW1hcnktaG92ZXIpO1xyXG4gICAgZmxleC1zaHJpbms6IDA7XHJcbn1cclxuPC9zdHlsZT4iXSwibWFwcGluZ3MiOiJBQWdDQSxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDO0FBQ3pCLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDO0FBQzVELENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQztBQUNyRDs7Ozs7Ozs7QUFKYztBQUsyQztBQUM1QjtBQUM3QjtBQUNBLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUMsQ0FBQyxDQUFDLENBQUM7Ozs7Ozs7Ozs7cUJBcENmLEtBQUssRUFBQyxtQkFBbUI7Ozs7Ozt3QkFEbEMsb0JBMEJRO0lBMUJELEtBQUssbUJBQUMsY0FBYyxrQkFBeUIsZ0JBQVM7O0lBQ3pELG9CQWlCTSxPQWpCTixVQWlCTTtRQWRTLGdCQUFTO3lCQUZwQixhQU9ZOztZQU5SLEtBQUssRUFBQyxrQkFBa0I7WUFFdkIsT0FBSyx1Q0FBRSxVQUFLOzs4QkFFYixDQUEyQjtjQUEzQixhQUEyQjtrQ0FBbEIsQ0FBUTtrQkFBUixhQUFROzs7O3lEQUFVLE9BRS9COzs7OztNQUNBLGFBT1k7UUFOUixLQUFLLEVBQUMscUJBQXFCO1FBQzNCLElBQUksRUFBSixFQUFJO1FBQ0gsT0FBSyx1Q0FBRSxnQkFBUyxJQUFJLGdCQUFTOzswQkFFOUIsQ0FBK0M7WUFBL0IsZ0JBQVM7NkJBQXpCLGFBQStDO2tDQUFwQixDQUFVO2tCQUFWLGFBQVU7Ozs7NkJBQ3JDLGFBQWtDO2tDQUFsQixDQUFRO2tCQUFSLGFBQVE7Ozs7Ozs7O29CQUloQyxhQUtFO01BSEcsYUFBYSxFQUFFLG9CQUFhO01BQzVCLG1CQUFpQixFQUFFLHNCQUFlO01BQ2xDLFFBQU0sdUNBQUUsVUFBSyxXQUFXLE1BQU07O2dCQUh0QixnQkFBUyIsImlnbm9yZUxpc3QiOltdfQ==