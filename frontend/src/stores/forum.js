import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '../axios'

export const useForumStore = defineStore('forum', () => {
  const posts = ref([])
  const postDetail = ref(null)
  const comments = ref([])
  const totalPosts = ref(0)
  const currentPage = ref(1)
  const isLoading = ref(false)
  const searchKeyword = ref('')
  const currentTag = ref('')

  const loadPosts = async (page = 1, keyword = '', tag = '') => {
    isLoading.value = true
    try {
      const params = new URLSearchParams({
        page,
        per_page: 10,
        search: keyword,
        tag
      })
      const res = await axios.get(`/api/forum/list?${params}`)
      if (page === 1) {
        posts.value = res.data.data
      } else {
        posts.value = [...posts.value, ...res.data.data]
      }
      totalPosts.value = res.data.total
      currentPage.value = page
      searchKeyword.value = keyword
      currentTag.value = tag
    } catch (e) {
      console.error('加载帖子失败:', e)
    } finally {
      isLoading.value = false
    }
  }

  const loadPostDetail = async (postId) => {
    try {
      const res = await axios.get(`/api/forum/detail/${postId}`)
      postDetail.value = res.data.data.post
      comments.value = res.data.data.comments
      return res.data.data
    } catch (e) {
      console.error('加载帖子详情失败:', e)
      throw e
    }
  }

  const createPost = async (formData) => {
    try {
      const res = await axios.post('/api/forum/post', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return res.data
    } catch (e) {
      console.error('发帖失败:', e)
      throw e
    }
  }

  const editPost = async (postId, data) => {
    try {
      const res = await axios.put(`/api/forum/post/${postId}`, data)
      return res.data
    } catch (e) {
      console.error('编辑帖子失败:', e)
      throw e
    }
  }

  const deletePost = async (postId) => {
    try {
      const res = await axios.delete(`/api/forum/post/${postId}`)
      posts.value = posts.value.filter(p => p.id !== postId)
      return res.data
    } catch (e) {
      console.error('删除帖子失败:', e)
      throw e
    }
  }

  const addComment = async (postId, content, parentId = null) => {
    try {
      const res = await axios.post(`/api/forum/comment/${postId}`, {
        content,
        parent_id: parentId
      })
      return res.data
    } catch (e) {
      console.error('发表评论失败:', e)
      throw e
    }
  }

  const likePost = async (postId) => {
    try {
      const res = await axios.post(`/api/forum/like/${postId}`)
      const post = posts.value.find(p => p.id === postId)
      if (post) {
        post.like_count = res.data.data.like_count
      }
      if (postDetail.value && postDetail.value.id === postId) {
        postDetail.value.like_count = res.data.data.like_count
        postDetail.value.user_liked = res.data.data.liked
      }
      return res.data
    } catch (e) {
      console.error('点赞失败:', e)
      throw e
    }
  }

  const bookmarkPost = async (postId) => {
    try {
      const res = await axios.post(`/api/forum/bookmark/${postId}`)
      if (postDetail.value && postDetail.value.id === postId) {
        postDetail.value.user_bookmarked = res.data.data.bookmarked
      }
      return res.data
    } catch (e) {
      console.error('收藏失败:', e)
      throw e
    }
  }

  const resetDetail = () => {
    postDetail.value = null
    comments.value = []
  }

  return {
    posts,
    postDetail,
    comments,
    totalPosts,
    currentPage,
    isLoading,
    searchKeyword,
    currentTag,
    loadPosts,
    loadPostDetail,
    createPost,
    editPost,
    deletePost,
    addComment,
    likePost,
    bookmarkPost,
    resetDetail
  }
})
