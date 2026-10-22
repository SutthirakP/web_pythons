# คำสั่ง GraphQL ทั้งหมด — graphql_demo

## เปิดใช้งาน

```powershell
uv run fastapi dev graphql_demo/main.py --port 8005
```

แล้วเปิด **`http://127.0.0.1:8005/graphql`** จะเจอหน้า GraphiQL: พิมพ์คำสั่งช่องซ้าย กดปุ่ม ▶ (หรือ `Ctrl+Enter`) ผลขึ้นช่องขวา

ข้อมูลตั้งต้นตอนตารางว่าง: `Iphone` (id 1), `IPAD` (id 2)

### ชื่อที่ใช้ได้ทั้งหมด

| ประเภท | ชื่อ | รับค่า | คืนค่า |
|---|---|---|---|
| Query | `products` | — | รายการ `Product` ทั้งหมด |
| Query | `product` | `id: Int!` | `Product` หรือ `null` ถ้าไม่มี |
| Mutation | `createProduct` | `name: String!`, `price: Float!` | `Product` ที่สร้าง |
| Mutation | `updateProduct` | `id: Int!`, `name: String`, `price: Float` | `Product` ที่แก้ หรือ `null` ถ้าไม่มี |
| Mutation | `deleteProduct` | `id: Int!` | `true` ลบสำเร็จ / `false` ไม่มี id นั้น |

`Product` มี field: `id`, `name`, `price`

`!` = บังคับต้องใส่ ไม่มี `!` = ใส่หรือไม่ใส่ก็ได้

> ในโค้ด Python ชื่อเป็น `create_product` แต่ใน GraphQL strawberry แปลงเป็น `createProduct` ให้อัตโนมัติ ต้องพิมพ์แบบ camelCase

---

## อ่านข้อมูล (Query)

### ดูสินค้าทั้งหมด

```graphql
query {
  products {
    id
    name
    price
  }
}
```

### ดูสินค้าตัวเดียวตาม id

```graphql
query {
  product(id: 1) {
    id
    name
    price
  }
}
```

ถ้าไม่มี id นั้นจะได้ `"product": null`

### เลือกเอาแค่บาง field

GraphQL คืนแค่ field ที่ขอ อยากได้แค่ชื่อก็ขอแค่ชื่อ:

```graphql
query {
  products {
    name
  }
}
```

---

## เพิ่ม / แก้ / ลบ (Mutation)

### เพิ่มสินค้า

```graphql
mutation {
  createProduct(name: "MacBook", price: 45900) {
    id
    name
    price
  }
}
```

**ไม่ต้องใส่ id** ระบบเลือกให้เองและไม่ซ้ำ โดยเลือกตามลำดับนี้:

1. **เลขที่ถูกลบไปล่าสุด** — เช่น มี 1–5 แล้วลบ 3 → ตัวใหม่ได้ id **3**
2. ถ้าลบไปหลายตัว จะเอา**ตัวที่ลบทีหลังสุดก่อน** — ลบ 1 แล้วลบ 3 → เพิ่มครั้งแรกได้ **3** ครั้งต่อไปได้ **1**
3. ถ้าไม่มีเลขที่ลบค้างไว้ แต่มีช่องว่างตรงกลาง (เช่น มี 1, 2, 4, 5) → ได้เลขที่ว่างที่น้อยที่สุด (**3**)
4. ถ้าไม่มีช่องว่างเลย → ได้เลขใหม่ต่อท้าย (มี 1–3 → ได้ **4**)

เลขที่ถูกลบเก็บไว้ในตาราง `freed_ids` (อยู่ใน `graphql.db` เดียวกัน) พอเอาเลขไปใช้แล้วก็ลบออกจากตารางนั้น

### แก้สินค้า — แก้ทั้งชื่อและราคา

```graphql
mutation {
  updateProduct(id: 1, name: "iPhone 17", price: 42900) {
    id
    name
    price
  }
}
```

### แก้สินค้า — แก้แค่ราคา

field ที่ไม่ใส่จะคงค่าเดิมไว้:

```graphql
mutation {
  updateProduct(id: 1, price: 39900) {
    id
    name
    price
  }
}
```

### แก้สินค้า — แก้แค่ชื่อ

```graphql
mutation {
  updateProduct(id: 1, name: "iPhone 17 Pro") {
    id
    name
    price
  }
}
```

ถ้าไม่มี id นั้นจะได้ `"updateProduct": null`

### ลบสินค้า

```graphql
mutation {
  deleteProduct(id: 3)
}
```

`deleteProduct` คืนค่า `true`/`false` เฉย ๆ ไม่ใช่ `Product` เลย**ไม่ต้อง**ใส่ `{ ... }` ต่อท้าย

---

## ใช้ตัวแปร (Variables)

วิธีที่หน้าเว็บ `/graphql-shop` ใช้จริง: เขียนคำสั่งครั้งเดียว แล้วส่งค่าแยกมาทีหลัง ไม่ต้องเอาค่าไปต่อ string เอง

**ช่อง query:**

```graphql
mutation Create($name: String!, $price: Float!) {
  createProduct(name: $name, price: $price) {
    id
    name
    price
  }
}
```

**ช่อง Variables** (แท็บด้านล่างของ GraphiQL):

```json
{
  "name": "AirPods",
  "price": 7990
}
```

อีกตัวอย่าง — แก้สินค้าด้วยตัวแปร:

```graphql
mutation Update($id: Int!, $name: String, $price: Float) {
  updateProduct(id: $id, name: $name, price: $price) {
    id
    name
    price
  }
}
```

```json
{
  "id": 2,
  "price": 30000
}
```

---

## ทริคเพิ่มเติม

### ขอหลายอย่างในครั้งเดียว (alias)

ชื่อ field ซ้ำกันในคำสั่งเดียวไม่ได้ ใช้ `ชื่อเล่น:` นำหน้าแยกกัน:

```graphql
query {
  first: product(id: 1) {
    name
    price
  }
  second: product(id: 2) {
    name
    price
  }
}
```

### ใช้ชุด field ซ้ำ (fragment)

```graphql
query {
  products {
    ...ProductInfo
  }
  product(id: 1) {
    ...ProductInfo
  }
}

fragment ProductInfo on Product {
  id
  name
  price
}
```

### หลาย mutation ในครั้งเดียว

mutation ในคำสั่งเดียวกันทำงาน**เรียงตามลำดับ**จากบนลงล่าง:

```graphql
mutation {
  a: createProduct(name: "Mouse", price: 590) {
    id
  }
  b: createProduct(name: "Keyboard", price: 1290) {
    id
  }
}
```

### ดูโครงสร้าง schema ทั้งหมด

```graphql
query {
  __schema {
    queryType {
      fields {
        name
      }
    }
    mutationType {
      fields {
        name
      }
    }
  }
}
```

หรือกดปุ่ม **Docs** ในหน้า GraphiQL ดูได้เลย

---

## ยิงจาก PowerShell (ไม่ใช้หน้าเว็บ)

GraphQL ส่งทุกคำสั่งเป็น `POST` ไป URL เดียว รูปแบบ body คือ `{ "query": "...", "variables": {...} }`

```powershell
# ดูสินค้าทั้งหมด
$body = @{ query = "{ products { id name price } }" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8005/graphql -Method Post -ContentType "application/json" -Body $body

# เพิ่มสินค้าด้วยตัวแปร
$body = @{
  query     = 'mutation Create($name: String!, $price: Float!) { createProduct(name: $name, price: $price) { id name price } }'
  variables = @{ name = "AirPods"; price = 7990 }
} | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8005/graphql -Method Post -ContentType "application/json" -Body $body
```

ใช้ `'...'` (single quote) ครอบคำสั่งที่มี `$` ไม่งั้น PowerShell จะแปลง `$name` เป็นตัวแปรของ PowerShell เอง

---

## Error ที่เจอบ่อย

| ข้อความ | สาเหตุ |
|---|---|
| `Cannot query field 'create_product' on type 'Mutation'` | ใช้ชื่อแบบ Python ต้องเป็น `createProduct` |
| `Field 'createProduct' argument 'price' of type 'Float!' is required` | ลืมใส่ค่าที่มี `!` |
| `Field 'products' of type '[Product!]!' must have a selection of subfields` | ลืม `{ id name price }` ต่อท้าย |
| `Field 'deleteProduct' must not have a selection since type 'Boolean!' has no subfields` | ใส่ `{ ... }` ต่อท้าย `deleteProduct` ซึ่งไม่ต้องใส่ |
| หน้าเว็บขึ้น "Failed to load products from GraphQL" | ยังไม่ได้เปิด backend พอร์ต 8005 |
