// Vercel serverless proxy: browser -> same-origin /api/foods -> Open Food Facts.
export default async function handler(req,res){
  if(req.method!=='GET'){res.setHeader('Allow','GET');return res.status(405).json({error:'Method not allowed'})}
  const q=typeof req.query.q==='string'?req.query.q.trim():'';
  if(q.length<3||q.length>100)return res.status(400).json({error:'Enter 3–100 characters'});
  const params=new URLSearchParams({search_terms:q,search_simple:'1',action:'process',json:'1',page_size:'60',tagtype_0:'countries',tag_contains_0:'contains',tag_0:'en:czech-republic',fields:'code,product_name,product_name_cs,brands,nutriments,countries_tags,langs_tags'});
  const controller=new AbortController();
  const timeout=setTimeout(()=>controller.abort(),12000);
  try{
    const response=await fetch('https://world.openfoodfacts.org/cgi/search.pl?'+params.toString(),{signal:controller.signal,headers:{'User-Agent':'NutriDenik/1.0 (personal nutrition diary; contact: https://github.com/lubos98/nutridiary)','Accept':'application/json'}});
    if(!response.ok)return res.status(502).json({error:'Open Food Facts HTTP '+response.status});
    const payload=await response.json();
    res.setHeader('Cache-Control','public, s-maxage=300, stale-while-revalidate=600');
    return res.status(200).json({products:Array.isArray(payload.products)?payload.products:[]});
  }catch(error){return res.status(502).json({error:error?.name==='AbortError'?'Open Food Facts timeout':'Open Food Facts connection failed'})}
  finally{clearTimeout(timeout)}
}
