param(
  [Parameter(Mandatory=$true)][string]$SourceJson
)

$ErrorActionPreference = 'Stop'
$siteRoot = $PSScriptRoot
$bookDir = Join-Path $siteRoot 'books'
$data = Get-Content -Raw -Encoding UTF8 -LiteralPath $SourceJson | ConvertFrom-Json
$works = @($data.works | Select-Object -First 100)

function ConvertTo-HtmlText([object]$value) {
  return [System.Net.WebUtility]::HtmlEncode([string]$value)
}

for ($page = 1; $page -le 10; $page++) {
  $start = ($page - 1) * 10
  $cards = [System.Text.StringBuilder]::new()

  for ($offset = 0; $offset -lt 10; $offset++) {
    $rank = $start + $offset + 1
    $book = $works[$start + $offset]
    $id = 'B{0:D3}' -f $rank
    $author = if ($book.authors.Count -gt 0) { $book.authors[0].name } else { 'Unknown author' }
    $year = if ($book.first_publish_year) { [int]$book.first_publish_year } else { 0 }
    $coverId = [string]$book.cover_id
    $coverUrl = if ($coverId) { "https://covers.openlibrary.org/b/id/$coverId-L.jpg" } else { "https://placehold.co/240x360/e9e9e9/777?text=No+Cover" }
    $price = 9000 + (($rank * 1370) % 21000)
    $listPrice = [math]::Ceiling(($price / 0.9) / 100) * 100
    $rating = '{0:N1}' -f (4.0 + (($rank * 7) % 10) / 10)
    $reviews = 18 + (($rank * 37) % 480)
    $point = [math]::Floor($price * 0.05 / 10) * 10
    $key = [string]$book.key
    $detailUrl = "https://openlibrary.org$key"
    $badge = if ($rank -le 20) { '<span class="badge best">베스트</span>' } else { '<span class="badge">추천</span>' }
    $delivery = if (($rank % 3) -eq 0) { '모레 도착 예정' } else { '내일 도착 예정' }
    [void]$cards.AppendLine(@"
<article class="book" data-id="$id" data-cover-id="$(ConvertTo-HtmlText $coverId)">
  <span class="rank">$rank</span>
  <a class="cover-link" href="$(ConvertTo-HtmlText $detailUrl)"><img class="cover" src="$(ConvertTo-HtmlText $coverUrl)" alt="$(ConvertTo-HtmlText $book.title) 책 표지" loading="lazy"></a>
  <div class="book-info"><div class="badges">$badge<span class="badge">무료배송</span></div>
    <a class="title" href="$(ConvertTo-HtmlText $detailUrl)">$(ConvertTo-HtmlText $book.title)</a>
    <p class="subtitle">오랫동안 사랑받아 온 세계 문학 클래식 에디션</p>
    <div class="author-line"><span class="author">$(ConvertTo-HtmlText $author)</span><span class="publisher">Open Library Edition</span><span class="published">$(ConvertTo-HtmlText $year)년 초판</span></div>
    <div class="review"><span class="rating" data-score="$rating">★ $rating</span> · 리뷰 $reviews</div>
  </div>
  <div class="price-box"><span class="discount">10%</span><span class="price">$($price.ToString('N0'))원</span><span class="list-price">$($listPrice.ToString('N0'))원</span><span class="point">적립금 $($point.ToString('N0'))원</span><span class="delivery">$delivery</span></div>
  <div class="actions"><button class="buy">바로구매</button><button class="cart">장바구니</button><button>♡ 찜하기</button></div>
</article>
"@)
  }

  $links = [System.Text.StringBuilder]::new()
  if ($page -gt 1) { [void]$links.Append("<a href=`"page$($page - 1).html`">‹ 이전</a>") }
  for ($p = 1; $p -le 10; $p++) {
    if ($p -eq $page) { [void]$links.Append("<span class=`"current`">$p</span>") }
    else { [void]$links.Append("<a href=`"page$p.html`">$p</a>") }
  }
  if ($page -lt 10) { [void]$links.Append("<a class=`"next`" rel=`"next`" href=`"page$($page + 1).html`">다음 ›</a>") }

  $html = @"
<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>세계문학 베스트셀러 $page | 북마켓</title><link rel="stylesheet" href="../assets/style.css"></head><body>
<div class="utility"><div class="utility-inner"><a href="#">로그인</a><a href="#">회원가입</a><a href="#">주문배송</a><a href="../guide.html">고객센터</a></div></div>
<header class="main-header"><div class="header-inner"><a class="logo" href="../index.html">BOOK<b>MARKET</b></a><form class="search"><input type="search" placeholder="찾고 싶은 책을 검색해 보세요" aria-label="도서 검색"><button type="submit">⌕</button></form><div class="header-icons"><a href="#"><span>♡</span>찜한 상품</a><a href="#"><span>🛒</span>장바구니</a></div></div></header>
<nav class="category-nav"><div class="nav-inner"><a class="all-menu" href="#">☰ 전체 카테고리</a><a href="page1.html">베스트</a><a href="#">신상품</a><a href="#">국내도서</a><a href="#">외국도서</a><a href="#">eBook</a><a class="hot" href="#">특가</a><a href="../guide.html">이벤트</a></div></nav>
<main><div class="breadcrumb">홈 &gt; 외국도서 &gt; 문학 &gt; 세계문학 베스트셀러</div><div class="content-head"><h1>세계문학 베스트셀러</h1><p>$page / 10 페이지 · 판매량 기준</p></div>
<div class="layout"><aside class="side"><h2>외국도서</h2><ul><li class="active">문학</li><li>인문/사회</li><li>경제/경영</li><li>과학/기술</li><li>예술</li><li>어린이</li><li>ELT/어학</li></ul></aside><section><div class="toolbar"><span>총 <strong>100</strong>개의 상품</span><div class="sort"><a class="on" href="#">판매량순</a><a href="#">신상품순</a><a href="#">낮은가격순</a><a href="#">평점순</a></div></div>
<div class="book-list">$($cards.ToString())</div><nav class="pagination" aria-label="페이지 이동">$($links.ToString())</nav></section></div></main>
<footer class="store-footer"><div class="footer-inner"><strong>BOOKMARKET</strong>㈜북마켓 · 대표자 홍길동 · 사업자등록번호 000-00-00000<br>본 사이트는 데이터구축실습을 위한 교육용 가상 서점이며 실제 결제는 이루어지지 않습니다. 도서 서지와 표지는 Open Library 자료를 사용합니다.</div></footer></body></html>
"@
  Set-Content -LiteralPath (Join-Path $bookDir "page$page.html") -Value $html -Encoding UTF8
}

Write-Output "Generated 10 pages and $($works.Count) book products."
