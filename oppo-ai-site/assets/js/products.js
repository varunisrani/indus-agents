document.addEventListener('DOMContentLoaded',function(){
  var grid=document.getElementById('product-grid');
  var search=document.getElementById('search');
  if(!grid) return;
  function render(products){
    grid.innerHTML='';
    products.forEach(function(p){
      var article=document.createElement('article');article.className='product-card';
      var img=document.createElement('img');img.src=p.images&&p.images[0]||'assets/images/products/product-placeholder.jpg';img.alt=p.name;img.loading='lazy';
      var h3=document.createElement('h3');h3.textContent=p.name;
      var pEl=document.createElement('p');pEl.textContent=p.shortDescription||'';
      article.appendChild(img);article.appendChild(h3);article.appendChild(pEl);
      grid.appendChild(article);
    })
  }
  fetch('data/products.json').then(function(r){if(!r.ok)throw new Error('no data');return r.json()}).then(function(data){render(data)}).catch(function(){/* keep static fallback */});
  if(search){search.addEventListener('input',function(){var q=search.value.toLowerCase();fetch('data/products.json').then(function(r){return r.json()}).then(function(data){render(data.filter(function(p){return p.name.toLowerCase().includes(q)|| (p.tags&&p.tags.join(' ').toLowerCase().includes(q))}))}).catch(function(){})})}
});