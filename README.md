# SocialNetwork
DRF app. Target: task.txt

<h4>Instruction</h4>
<p>App with <a href='https://jwt.io/introduction'>JWT</a> authentification. After user loged in you got two tokens (access and refresh). Steps with sign {auth}  require token. Also statistis points require {admin} permisions.</p>
<ul>
  <li>User sign up, <strong>post: /api/user/new/</strong>, required: 'username' and 'password' (there are Django requirements for both fields).</li>
  <li>User log in, <strong>post: /api/user/login/</strong>, required: 'username' and 'password' , user should be created. </li>
  <li>User refresh token, <strong>post: /api/user/refresh/</strong>, required: 'access' token. </li>
  <li>{auth} Post creation, <strong>post: /api/post/new/</strong>, required: 'title' and 'body'.</li>
  <li>{auth} Get list with posts, <strong>get: /api/post/all/</strong>.</li>
  <li>{auth} Process like-dislike for particular post: <strong>post: /api/post/{int:id}/</strong>, required: 'kind' ('like' or 'dislike')' (One user can 'like-dislike' particular post only one time).</li>
  <li>{auth}{admin} All user statistics (get last login and last request to service), <strong>get: /api/user/stat/all/</strong>, (last login - when user logged in and got token pairs, last request - last not anonimous request).</li>
  <li>{auth}{admin} Particular user statistic (get last login and last request to service), <strong>get: /api/user/stat/{int:id}/</strong>.</li>
  <li>{auth}{admin} Analytics about 'like-dislike' process, <strong>get: /api/analytics/ </strong>. This point shows information about 'like-dislike' quantity by day. Filters are available: 'date_from', 'date_to', example: /api/analytics/?date_from=2021-02-02&date_to=2021-02-15.</li>
</ul>
<p>All decisions for API made for particular task. There are comments in code.</p>
<p>If someone has a questions or comments, please, let me know.</p>


