from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.utils.security import generate_license_key
from app.routers.auth import get_current_user

router = APIRouter(prefix="/licenses")

@router.post("/", response_model=schemas.License)
def create_license(
    license_data: schemas.LicenseCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # สร้าง license key
    license_key = generate_license_key()
    
    # สร้าง license ใหม่
    db_license = models.License(
        key=license_key,
        expires_at=license_data.expires_at,
        allowed_ips=license_data.allowed_ips,
        owner_id=current_user.id
    )
    
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    
    return db_license

@router.get("/", response_model=List[schemas.License])
def read_licenses(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    licenses = db.query(models.License).filter(
        models.License.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return licenses

@router.post("/verify", response_model=dict)
def verify_license(
    verify_data: schemas.LicenseVerify,
    db: Session = Depends(get_db)
):
    # ค้นหา license
    license = db.query(models.License).filter(
        models.License.key == verify_data.license_key,
        models.License.is_active == True
    ).first()
    
    if not license:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or inactive license"
        )
    
    # ตรวจสอบวันหมดอายุ
    if license.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="License has expired"
        )
    
    # ตรวจสอบ IP (ถ้ามีการกำหนด)
    if license.allowed_ips and verify_data.ip_address:
        allowed_ip_list = [ip.strip() for ip in license.allowed_ips.split(",")]
        if verify_data.ip_address not in allowed_ip_list:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP address not allowed for this license"
            )
    
    # ค้นหาหรือสร้างการเปิดใช้งาน
    activation = db.query(models.Activation).filter(
        models.Activation.license_id == license.id,
        models.Activation.machine_id == verify_data.machine_id
    ).first()
    
    if not activation:
        # สร้างการเปิดใช้งานใหม่
        activation = models.Activation(
            license_id=license.id,
            ip_address=verify_data.ip_address,
            machine_id=verify_data.machine_id
        )
        db.add(activation)
    else:
        # อัปเดตเวลาเช็คอินล่าสุด
        activation.last_check_in = datetime.utcnow()
        if verify_data.ip_address:
            activation.ip_address = verify_data.ip_address
    
    db.commit()
    
    return {
        "valid": True,
        "expires_at": license.expires_at,
        "message": "License is valid"
    }